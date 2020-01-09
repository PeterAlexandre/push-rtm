import json

from django.http import HttpResponse
from django.conf import settings
from django.views.generic import View
from django.http import JsonResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404

from smartmin.views import SmartReadView, SmartTemplateView

from ureport.polls.models import Poll, PollQuestion
from ureport.polls_global.models import PollGlobal, PollGlobalSurveys
from ureport.polls.templatetags.ureport import question_segmented_results
from ureport.settings import AVAILABLE_COLORS


class PollReadView(SmartReadView):
    template_name = "results/poll_result.html"
    permission = "polls.poll_list"
    model = Poll

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["org"] = self.request.org
        context["poll"] = self.get_object()
        context["sdgs"] = settings.SDG_LIST
        return context

    def derive_queryset(self):
        queryset = super(PollReadView, self).derive_queryset()
        queryset = queryset.filter(is_active=True, has_synced=True)
        if not self.request.user.is_superuser:
            queryset = queryset.filter(org=self.request.org)
        return queryset


class PollQuestionResultsView(SmartReadView):
    model = PollQuestion

    def derive_queryset(self):
        queryset = super(PollQuestionResultsView, self).derive_queryset()
        queryset = queryset.filter(poll__org=self.request.org, is_active=True)
        return queryset

    def render_to_response(self, context, **kwargs):
        segment = self.request.GET.get("segment", None)
        if segment:
            segment = json.loads(segment)

        results = self.object.get_results(segment=segment)

        return HttpResponse(json.dumps(results))


class PollGlobalReadView(SmartTemplateView):
    template_name = "results/global_poll_result.html"
    model = PollGlobal

    def calculate_percent_participating_unct(self, active_uncts, all_uncts):
        return int((active_uncts * 100) / all_uncts) if all_uncts > 0 else 0

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        poll_global = get_object_or_404(PollGlobal, pk=self.kwargs["pk"])

        polls_local = []
        polls_global_surveys = poll_global.polls_global.filter(is_joined=True)
        all_sdgs_arrays = polls_global_surveys.values_list('poll_local__questions__sdgs', flat=True)

        all_orgs = []
        active_orgs = []
        for poll_local_iterator in polls_global_surveys:
            polls_local.append(poll_local_iterator.poll_local)

            org = poll_local_iterator.poll_local.org
            all_orgs.append(org)
            if org.is_active:
                active_orgs.append(org)

        all_sdgs = []
        for sdg_array in all_sdgs_arrays:
            [all_sdgs.append(sdg) for sdg in sdg_array]

        all_sdgs = list(set(all_sdgs))
        all_sdgs.sort()

        all_orgs = len(set(all_orgs))
        active_orgs = len(set(active_orgs))

        context["poll_initial"] = polls_local[0].id if len(polls_local) > 0 else -1
        context["participating_unct"] = self.calculate_percent_participating_unct(active_orgs, all_orgs)
        context["poll_global"] = poll_global
        context["all_local_polls"] = list(polls_local)
        context["num_countries"] = len(polls_local)
        context["sdgs"] = settings.SDG_LIST
        context["all_sdgs"] = all_sdgs
        return context


class PollGlobalDataView(View):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._response = {}
        self._global_questions = {}
        self._local_questions = []

    def _get_question_segmented_results(self, question, tag):
        """
        Get question data sorted by tag.
        Tag's example: All, Age, Gender.
        """
        return question_segmented_results(question, tag)

    def _get_formated_question_segmented_results(self, question, tag):
        """
        Get the segmented data and format in a dictionary.
        Dictionary data is used for graphics in template.
        """
        results = self._get_question_segmented_results(question, tag)
        categories = []
        series = []
        label = []
        data = []
        for result in results:
            categories.append(result.get("label"))

            for category in result.get("categories"):
                if category.get("label") not in label:
                    label.append(category.get("label"))
                    data.append([category.get("count"), ])
                else:
                    index_label = label.index(category.get("label"))
                    data[index_label].append(category.get("count"))

        for item in label:
            series.append({
                "label": item,
                "data": data[label.index(item)],
                "backgroundColor": AVAILABLE_COLORS[label.index(item)],
                "borderColor": "rgba(255, 255, 255, 0.1)",
            })

        dict_result = {
            "categories": categories,
            "series": series
        }
        return dict_result

    def _sum_values_arrays(self, array_one, array_two):
        """Sum values ​​from two arrays."""
        return list(map(lambda x, y: x + y, array_one, array_two))

    def _generate_global_data(self, question, tag):
        """Get data from a specific question and add to the overall results."""
        question_dict = self._global_questions.get(question.ruleset_label)
        values = question_dict.get(tag).get('series')
        values_to_return = []
        for value in values:
            current_value = value.get('data')
            loop_value = self._get_formated_question_segmented_results(question, tag).get('series')[values.index(value)].get(
                'data')
            new_values_in_array = self._sum_values_arrays(current_value, loop_value)
            values_to_return.append(new_values_in_array)

        return values_to_return

    def _update_global_data(self, question, tag):
        """Get the data of a question added to the global ones and update data global."""
        new_values = self._generate_global_data(question, tag)
        for values in new_values:
            self._global_questions[question.ruleset_label][tag]['series'][new_values.index(values)]['data'] = values

        return self._global_questions

    def get(self, request, *args, **kwargs):
        global_survey = self.kwargs["pk"]
        unct = self.kwargs["unct"]

        global_poll_local_id = PollGlobalSurveys.objects.filter(
            poll_global=global_survey,
            is_joined=True
        ).values_list(
            'poll_local_id',
            flat=True
        )

        global_polls_questions = PollQuestion.objects.filter(
            is_active=True,
            poll_id__in=list(global_poll_local_id),
            poll__is_active=True
        )

        response = dict()

        for question in global_polls_questions:
            formated_segmented_results_age = self._get_formated_question_segmented_results(question, "age")
            formated_segmented_results_gender = self._get_formated_question_segmented_results(question, "gender")

            statistics = {}
            word_cloud = []
            if question.is_open_ended():
                for category in question.get_results()[0].get("categories"):
                    count = category.get("count")
                    word_cloud.append(
                        {
                            "text": category.get("label").upper(),
                            "size": count if count > 10 else 20 + count
                        }
                    )
            else:
                labels = []
                series = []
                counts = []

                results = question.get_results()[0]
                categories = results.get("categories")
                for category in categories:
                    labels.append(category.get("label"))
                    series.append("{0:.0f}".format(category.get("count") / results.get("set") * 100))
                    counts.append(category.get("count"))

                statistics["labels"] = labels
                statistics["series"] = series
                statistics["counts"] = counts

            question_dict = self._global_questions.get(question.ruleset_label)

            if question_dict:
                values_in_array_statistics = question_dict.get('statistics').get('counts')
                new_values_in_array_statistics = self._sum_values_arrays(values_in_array_statistics, counts)
                self._global_questions[question.ruleset_label]['statistics']['counts'] = new_values_in_array_statistics

                self._update_global_data(question, 'age')
                self._update_global_data(question, 'gender')

            else:
                self._global_questions[question.ruleset_label] = ({
                    "id": question.pk,
                    "is_active": question.is_active,
                    "created_on": question.created_on,
                    "modified_on": question.modified_on,
                    "title": question.title,
                    "created_by_id": question.created_by_id,
                    "modified_by_id": question.modified_by_id,
                    "poll_id": question.poll_id,
                    "ruleset_label": question.ruleset_label,
                    "url": reverse("results.poll_read", args=[question.poll.pk]),
                    "is_open_ended": question.is_open_ended(),
                    "word_cloud": word_cloud,
                    "get_responded": question.get_responded(),
                    "get_polled": question.get_polled(),
                    "sdgs": question.sdgs,
                    "statistics": statistics,
                    "age": formated_segmented_results_age,
                    "gender": formated_segmented_results_gender
                })

        local_poll_questions = PollQuestion.objects.filter(is_active=True, poll_id__in=unct, poll__is_active=True)
        local_poll_title = local_poll_questions[0].poll.title if local_poll_questions else None

        for question in local_poll_questions:
            formated_segmented_results_age = self._get_formated_question_segmented_results(question, "age")
            formated_segmented_results_gender = self._get_formated_question_segmented_results(question, "gender")

            statistics = {}
            word_cloud = []
            if question.is_open_ended():
                for category in question.get_results()[0].get("categories"):
                    count = category.get("count")
                    word_cloud.append(
                        {"text": category.get("label").upper(), "size": count if count > 10 else 20 + count}
                    )
            else:
                labels = []
                series = []
                counts = []

                results = question.get_results()[0]
                categories = results.get("categories")
                for category in categories:
                    labels.append(category.get("label"))
                    series.append("{0:.0f}".format(category.get("count") / results.get("set") * 100))
                    counts.append(category.get("count"))

                statistics["labels"] = labels
                statistics["series"] = series
                statistics["counts"] = counts

            self._local_questions.append(
                {
                    "id": question.pk,
                    "is_active": question.is_active,
                    "created_on": question.created_on,
                    "modified_on": question.modified_on,
                    "title": question.title,
                    "created_by_id": question.created_by_id,
                    "modified_by_id": question.modified_by_id,
                    "poll_id": question.poll_id,
                    "ruleset_label": question.ruleset_label,
                    "url": reverse("results.poll_read", args=[question.poll.pk]),
                    "is_open_ended": question.is_open_ended(),
                    "word_cloud": word_cloud,
                    "get_responded": question.get_responded(),
                    "get_polled": question.get_polled(),
                    "sdgs": question.sdgs,
                    "statistics": statistics,
                    "age": formated_segmented_results_age,
                    "gender": formated_segmented_results_gender,
                    "local_poll_title": local_poll_title,
                }
            )

        response['questions_global'] = self._global_questions
        response['questions_local'] = self._local_questions
        response['number_questions'] = len(self._local_questions)
        response['sdgs'] = dict(settings.SDG_LIST)

        return JsonResponse(response)
