# coding=utf-8
from flask_wtf import Form as Form_base
from wtforms import (
    BooleanField,
    DateField,
    PasswordField,
    TextAreaField,
    TextField,
    SelectField,
)
from wtforms.validators import Optional, ValidationError

from art17.common import DEFAULT_MS
from art17.models import (
    Dataset,
    EtcDicMethod,
    EtcDicConclusion,
    EtcDicPopulationUnit,
    EtcDataSpeciesRegion,
    EtcDataHabitattypeRegion,
)
from art17.utils import validate_field, validate_ref, validate_nonempty

EMPTY_FORM = "Please fill at least one field"
NOT_NUMERIC_VALUES = (
    "Only numeric values with not more than two decimals are accepted!"
)
METH_CONCL_MANDATORY = "At least one method and conclusion must be filled!"
METH_CONCL_PAIR_MANDATORY = "You cannot add a conclusion without a method, " \
    "nor a method without a conclusion"
INVALID_MS_REGION_PAIR = "Please select an MS country code that is available " \
    "for the selected region"

NATURE_CHOICES = [('', ''), ('y', 'yes'), ('n', 'no'), ('nc', 'nc')]
CONTRIB_METHODS = [
    ('A', 'A'), ('A+', 'A+'), ('B1', 'B1'), ('B2', 'B2'), ('C', 'C'), ('D', 'D'), ('E', 'E'),
]
CONTRIB_TYPE = [
    ('+', '+'), ('-', '-'), ('=', '='), ('x', 'x')
]
CONCL_TYPE = [
    ('+', '+'), ('-', '-'), ('0', '0'), ('x', 'x')
]

PROSPECTS_CHOICES = [('', ''), ('good', 'good'), ('poor', 'poor'), ('bad', 'bad'), ('unk', 'unk')]

ZERO_METHODS = [('00', '00'), ('0', '0')]


def all_fields(form):
    for field in form:
        if hasattr(field, 'form'):
            for subfield in all_fields(field.form):
                yield subfield
        else:
            yield field


def numeric_validation(form, field):
    """ Default validation in previous app
    """
    if not validate_field(field.data):
        raise ValidationError(NOT_NUMERIC_VALUES)


def ref_validation(form, field):
    if not validate_ref(field.data):
        raise ValidationError(NOT_NUMERIC_VALUES)


def species_ms_validator(form, field):
    member_states = (
        EtcDataSpeciesRegion.query
        .with_entities(
            EtcDataSpeciesRegion.eu_country_code
        )
        .filter_by(
            region=form.region.data,
            subject=form.kwargs['subject'],
            dataset_id=form.kwargs['period'])
        .all())
    member_states = [ms[0] for ms in member_states]
    member_states.append(DEFAULT_MS)
    if field.data not in member_states:
        raise ValidationError(INVALID_MS_REGION_PAIR)


def habitat_ms_validator(form, field):
    member_states = (
        EtcDataHabitattypeRegion.query
        .with_entities(
            EtcDataHabitattypeRegion.eu_country_code
        )
        .filter_by(
            region=form.region.data,
            subject=form.kwargs['subject'],
            dataset_id=form.kwargs['period'])
        .all())
    member_states = [ms[0] for ms in member_states]
    member_states.append(DEFAULT_MS)
    if field.data not in member_states:
        raise ValidationError(INVALID_MS_REGION_PAIR)


def form_validation(form, field):
    """ Validate form as a whole: no empty data, no data without conclusion etc
    """
    excluded = [form.region]
    if hasattr(form, 'MS'):
        excluded.append(form.MS)
    fields = [f for f in all_fields(form) if f not in excluded]
    empty = [f for f in fields if not f.data]

    if empty and len(empty) == len(fields):
        raise ValidationError(EMPTY_FORM)


class OptionalSelectField(SelectField):

    def __init__(self, validators=None, default=None, **kwargs):
        validators = validators or [Optional()]
        default = default or ''
        super(OptionalSelectField, self).__init__(validators=validators,
                                                  default=default, **kwargs)


class Form(Form_base):
    def validate(self, **kwargs):
        if not super(Form, self).validate():
            return False

        return self.custom_validate(**kwargs)

    def custom_validate(self, **kwargs):
        return True


class CommonFilterForm(Form):

    period = SelectField('Period...')
    group = SelectField('Group...')
    region = SelectField('Bio-region...')

    def __init__(self, *args, **kwargs):
        super(CommonFilterForm, self).__init__(*args, **kwargs)
        self.period.choices = [(d.id, d.name) for d in Dataset.query.all()]


class SummaryFilterForm(CommonFilterForm):

    subject = SelectField('Name...')


class ReportFilterForm(CommonFilterForm):

    country = SelectField('Country...')


class _OptionsBase(object):

    def get_method_options(self, methods):
        return [
            (a, b)
            for (a, b) in methods
            if not a or a.startswith('1') or (a.startswith('2') and a !=
                                              self.EXCLUDE2)
        ]

    def get_sf_options(self, methods):
        return [
            (a, b)
            for (a, b) in methods
            if not a or (a.startswith('2') and a != self.EXCLUDE2)
        ]

    def get_assesm_options(self, methods):
        return [
            (a, b)
            for (a, b) in methods
            if not a or (a.startswith('3') and a != self.EXCLUDE3) or a == 'MTX'
        ]

    def filter_conclusions(self, conclusions):
        output = []
        for conclusion, value in conclusions:
            if conclusion.strip() == 'XU':
                continue
            elif not conclusion.endswith('?') and not conclusion == 'NA':
                output.append((conclusion, value))
        return output


class OptionsBaseSpecies(_OptionsBase):

    EXCLUDE2 = '2XA'
    EXCLUDE3 = '3XA'


class OptionsBaseHabitat(_OptionsBase):

    EXCLUDE2 = '2XP'
    EXCLUDE3 = '3XP'


class SummaryFormMixin(object):

    form_errors = TextField(validators=[form_validation])

    def setup_choices(self, dataset_id):
        pass

    def all_errors(self):
        errors = []
        for field_name, field_errors in self.errors.iteritems():
            errors.extend(field_errors)
        errors = set(errors)
        text = '<ul>'
        for error in errors:
            text += '<li>' + error + '</li>'
        text += '</ul>'
        return text


class SummaryManualFormSpecies(Form, OptionsBaseSpecies, SummaryFormMixin):

    region = SelectField(default='')

    range_surface_area = TextField(default=None,
                                   validators=[numeric_validation])
    method_range = OptionalSelectField()
    conclusion_range = OptionalSelectField()
    range_trend = OptionalSelectField()
    complementary_favourable_range = TextField(validators=[ref_validation])

    population_minimum_size = TextField(validators=[numeric_validation])
    population_maximum_size = TextField(validators=[numeric_validation])
    population_best_value = TextField(validators=[numeric_validation])
    population_unit = OptionalSelectField()
    method_population = OptionalSelectField()
    conclusion_population = OptionalSelectField()
    population_trend = OptionalSelectField()
    complementary_favourable_population = TextField(validators=[ref_validation])
    complementary_favourable_population_unit = OptionalSelectField()

    method_habitat = OptionalSelectField()
    conclusion_habitat = OptionalSelectField()
    habitat_trend = OptionalSelectField()

    future_range = OptionalSelectField()
    future_population = OptionalSelectField()
    future_habitat = OptionalSelectField()
    method_future = OptionalSelectField()
    conclusion_future = OptionalSelectField()

    method_assessment = OptionalSelectField()
    conclusion_assessment = OptionalSelectField()
    conclusion_assessment_trend = OptionalSelectField()
    conclusion_assessment_prev = OptionalSelectField()
    conclusion_assessment_trend_prev = OptionalSelectField()
    conclusion_assessment_change = OptionalSelectField()
    conclusion_assessment_trend_change = OptionalSelectField()

    method_target1 = OptionalSelectField()
    backcasted_2007 = OptionalSelectField()

    def setup_choices(self, dataset_id):
        empty = [('', '')]
        methods = [a[0] for a in EtcDicMethod.all(dataset_id)]
        methods = empty + zip(methods, methods)
        conclusions = [a[0] for a in EtcDicConclusion.all(dataset_id) if a[0]]
        conclusions = empty + zip(conclusions, conclusions)
        conclusions = self.filter_conclusions(conclusions)
        #trends = [a[0] for a in EtcDicTrend.all(dataset_id) if a[0]]
        #trends = empty + zip(trends, trends)
        trends = empty + CONCL_TYPE
        units = [a for a in EtcDicPopulationUnit.all(dataset_id) if a[0]]
        units = empty + units

        self.region.choices = empty

        self.method_range.choices = (
            ZERO_METHODS + self.get_method_options(methods)
        )

        self.population_unit.choices = [('', ''), ('i', 'i')]

        self.method_population.choices = (
            ZERO_METHODS + self.get_method_options(methods)
        )

        self.complementary_favourable_population_unit.choices = [('', ''), ('i', 'i')]
        self.method_habitat.choices = (
            ZERO_METHODS + self.get_method_options(methods)
        )

        self.future_range.choices = PROSPECTS_CHOICES
        self.future_population.choices = PROSPECTS_CHOICES
        self.future_habitat.choices = PROSPECTS_CHOICES
        self.method_future.choices = ZERO_METHODS + self.get_sf_options(methods)
        self.method_assessment.choices = self.get_assesm_options(methods)
        self.method_target1.choices = empty + CONTRIB_METHODS

        for f in (self.range_trend, self.population_trend, self.habitat_trend):
            f.choices = trends
        for f in (self.conclusion_range, self.conclusion_population,
                  self.conclusion_habitat, self.conclusion_future,
                  self.conclusion_assessment, self.conclusion_assessment_prev, self.backcasted_2007):
            f.choices = conclusions
        self.conclusion_assessment_change.choices = NATURE_CHOICES
        self.conclusion_assessment_trend_change.choices = NATURE_CHOICES
        self.conclusion_assessment_trend.choices = empty + CONTRIB_TYPE
        self.conclusion_assessment_trend_prev.choices = empty + CONTRIB_TYPE

    def custom_validate(self, **kwargs):
        method_conclusions = [
            (self.method_range, self.conclusion_range),
            (self.method_population, self.conclusion_population),
            (self.method_habitat, self.conclusion_habitat),
            (self.method_future, self.conclusion_future),
            (self.method_assessment, self.conclusion_assessment),
        ]
        one = False
        for m, c in method_conclusions:
            mc, cc = m.data, c.data
            if mc and not cc:
                c.errors.append(METH_CONCL_PAIR_MANDATORY)
            elif cc and not mc:
                m.errors.append(METH_CONCL_PAIR_MANDATORY)
            elif mc and cc:
                one = True
        if not one:
            self.form_errors.errors.append(METH_CONCL_MANDATORY)

        return not self.errors


class SummaryManualFormSpeciesSTA(SummaryManualFormSpecies):

    MS = SelectField(default='', validators=[species_ms_validator])


class SummaryManualFormHabitat(Form, OptionsBaseHabitat, SummaryFormMixin):

    region = SelectField()

    range_surface_area = TextField(validators=[numeric_validation])
    method_range = OptionalSelectField()
    conclusion_range = OptionalSelectField()
    range_trend = OptionalSelectField()
    range_yearly_magnitude = TextField()
    complementary_favourable_range = TextField(validators=[ref_validation])

    coverage_surface_area = TextField(validators=[numeric_validation])
    method_area = OptionalSelectField()
    conclusion_area = OptionalSelectField()
    coverage_trend = OptionalSelectField()
    coverage_yearly_magnitude = TextField()
    complementary_favourable_area = TextField(validators=[ref_validation])

    method_structure = OptionalSelectField()
    conclusion_structure = OptionalSelectField()

    method_future = OptionalSelectField()
    conclusion_future = OptionalSelectField()

    method_assessment = OptionalSelectField()
    conclusion_assessment = OptionalSelectField()
    conclusion_assessment_trend = OptionalSelectField()
    conclusion_assessment_prev = OptionalSelectField()
    conclusion_assessment_change = OptionalSelectField()

    method_target1 = OptionalSelectField()
    conclusion_target1 = OptionalSelectField()

    def setup_choices(self, dataset_id):
        empty = [('', '')]
        methods = [a[0] for a in EtcDicMethod.all(dataset_id)]
        methods = empty + zip(methods, methods)
        conclusions = [a[0] for a in EtcDicConclusion.all(dataset_id) if a[0]]
        conclusions = empty + zip(conclusions, conclusions)
        conclusions = self.filter_conclusions(conclusions)
        #trends = [a[0] for a in EtcDicTrend.all(dataset_id) if a[0]]
        #trends = empty + zip(trends, trends)
        trends = empty + CONCL_TYPE

        self.region.choices = empty

        self.method_range.choices = (
            ZERO_METHODS + self.get_method_options(methods)
        )
        self.method_area.choices = (
            ZERO_METHODS + self.get_method_options(methods)
        )

        self.method_structure.choices = ZERO_METHODS + self.get_sf_options(methods)
        self.method_future.choices = ZERO_METHODS + self.get_sf_options(methods)
        self.method_assessment.choices = self.get_assesm_options(methods)
        self.method_target1.choices = empty + CONTRIB_METHODS

        for f in (self.range_trend, self.coverage_trend,
                  self.conclusion_assessment_trend):
            f.choices = trends
        for f in (self.conclusion_range, self.conclusion_area,
                  self.conclusion_structure, self.conclusion_future,
                  self.conclusion_assessment,
                  self.conclusion_assessment_prev):
            f.choices = conclusions
        self.conclusion_assessment_change.choices = NATURE_CHOICES
        self.conclusion_assessment_trend.choices = empty + CONTRIB_TYPE
        self.conclusion_target1.choices = empty + CONTRIB_TYPE

    def custom_validate(self, **kwargs):
        method_conclusions = [
            (self.method_range, self.conclusion_range),
            (self.method_area, self.conclusion_area),
            (self.method_structure, self.conclusion_structure),
            (self.method_future, self.conclusion_future),
            (self.method_assessment, self.conclusion_assessment),
            (self.method_target1, self.conclusion_target1),
        ]
        one = False
        for m, c in method_conclusions:
            mc, cc = m.data, c.data
            if mc and not cc:
                c.errors.append(METH_CONCL_PAIR_MANDATORY)
            elif cc and not mc:
                m.errors.append(METH_CONCL_PAIR_MANDATORY)
            elif mc and cc:
                one = True
        if not one:
            self.form_errors.errors.append(METH_CONCL_MANDATORY)

        return not self.errors


class SummaryManualFormHabitatSTA(SummaryManualFormHabitat):

    MS = SelectField(default='', validators=[habitat_ms_validator])


class SummaryManualFormSpeciesRef(Form, SummaryFormMixin):

    region = SelectField()

    complementary_favourable_range = TextField(validators=[ref_validation])
    complementary_favourable_population = TextField(validators=[ref_validation])
    complementary_favourable_population_unit = OptionalSelectField()

    def setup_choices(self, dataset_id):
        self.complementary_favourable_population_unit.choices = [('', ''), ('i', 'i')]

class SummaryManualFormSpeciesRefSTA(SummaryManualFormSpeciesRef):

    MS = SelectField(default='', validators=[Optional(), species_ms_validator])


class SummaryManualFormHabitatRef(Form, SummaryFormMixin):

    region = SelectField()

    complementary_favourable_range = TextField(validators=[ref_validation])
    complementary_favourable_area = TextField(validators=[ref_validation])


class SummaryManualFormHabitatRefSTA(SummaryManualFormHabitatRef):

    MS = SelectField(default='', validators=[Optional(), habitat_ms_validator])


class ProgressFilterForm(Form):

    period = SelectField('Period...')
    group = SelectField('Group...')
    conclusion = SelectField('Conclusion...')
    assessor = SelectField('Assessor...')
    extra = BooleanField('Details')

    def __init__(self, *args, **kwargs):
        super(ProgressFilterForm, self).__init__(*args, **kwargs)
        self.period.choices = [(d.id, d.name) for d in Dataset.query.all()]


class WikiEditForm(Form):

    text = TextAreaField()

    def custom_validate(self):
        return validate_nonempty(self.text.data)


class CommentForm(Form):

    comment = TextAreaField()

    def custom_validate(self):
        return validate_nonempty(self.comment.data)


class ConfigForm(Form):
    start_date = DateField(label="Start date (YYYY-MM-DD)",
                           validators=[Optional()])
    end_date = DateField(label="End date (YYYY-MM-DD)",
                         validators=[Optional()])
    admin_email = TextField(label="Administrator email (space separated list)",
                            validators=[Optional()])
    default_dataset_id = SelectField(label="Default period")

    species_map_url = TextField(label="URL for species map",
                                validators=[Optional()])
    sensitive_species_map_url = TextField(
        label="URL for sensitive species map", validators=[Optional()])
    habitat_map_url = TextField(label="URL for habitat map",
                                validators=[Optional()])

    def __init__(self, *args, **kwargs):
        super(ConfigForm, self).__init__(*args, **kwargs)
        dataset_qs = Dataset.query.with_entities(Dataset.id, Dataset.name).all()
        self.default_dataset_id.choices = [
            (str(ds_id), name) for ds_id, name in dataset_qs
        ]


class ChangeDetailsForm(Form):
    institution = TextField(label="Institution", validators=[Optional()])
    abbrev = TextField(label="Abbreviation", validators=[Optional()])
    MS = TextField(label="MS", validators=[Optional()])
    qualification = TextField(label="Qualification", validators=[Optional()])
