from flask.ext.script import Manager, Option
from flask.ext.security.script import Command

from art17 import models


class GenerateNewPeriodCommand(Command):

    option_list = Command.option_list + [
        Option('-s', '--schema', dest='schema', required=True),
        Option('-n', '--name', dest='name', required=True)
    ]

    def run(self, **kwargs):

        dataset = models.Dataset.query.filter_by(schema=kwargs['schema']).first()

        if not dataset:
            dataset = models.Dataset(
                schema=kwargs['schema'],
                name=kwargs['name'],
            )
            models.db.session.add(dataset)
            models.db.session.commit()
        
        print("Importing EtcDicMethod...")
        etc_dic_methods = models.EtcDicMethod.query.all()
        for method in etc_dic_methods:
            if not models.EtcDicMethod.query.filter_by(
                method=method.method, dataset_id=dataset.id).all():
                new_method = models.EtcDicMethod(
                    order=method.order,
                    method=method.method,
                    details=method.details,
                    dataset_id=dataset.id,
                )
                models.db.session.add(new_method)
                models.db.session.commit()

        print("Importing EtcDicBiogeoregs...")
        etc_dic_biogeoregs = models.EtcDicBiogeoreg.query.all()
        for biogeoreg in etc_dic_biogeoregs:
            if not models.EtcDicBiogeoreg.query.filter_by(
                    reg_code=biogeoreg.reg_code, dataset_id=dataset.id).all():
                new_biogeoreg = models.EtcDicBiogeoreg(
                    reg_code=biogeoreg.reg_code,
                    reg_name=biogeoreg.reg_name,
                    ordine=biogeoreg.ordine,
                    order=biogeoreg.order,
                    dataset_id=dataset.id,
                )
                models.db.session.add(new_biogeoreg)
                models.db.session.commit()

        print("Importing EtcDicConclusions...")
        etc_dic_conclusions = models.EtcDicConclusion.query.all()
        for conclusion in etc_dic_conclusions:
            if not models.EtcDicConclusion.query.filter_by(
                    conclusion=conclusion.conclusion, dataset_id=dataset.id).all():
                new_conclusion = models.EtcDicConclusion(
                    order=conclusion.order,
                    conclusion=conclusion.conclusion,
                    details=conclusion.details,
                    dataset_id=dataset.id
                )
                models.db.session.add(new_conclusion)
                models.db.session.commit()

        print("Importing EtcDicDecision...")
        etc_dic_decisions = models.EtcDicDecision.query.all()
        for decision in etc_dic_decisions:
            if not models.EtcDicDecision.query.filter_by(
                    decision=decision.decision, dataset_id=dataset.id).all():
                new_decision = models.EtcDicDecision(
                    order=decision.order,
                    decision=decision.decision,
                    details=decision.details,
                    dataset_id=dataset.id,
                )
                models.db.session.add(new_decision)
                models.db.session.commit()

        print("Importing EtcDicPopulationUnit...")
        etc_dic_population_units = models.EtcDicPopulationUnit.query.all()
        for unit in etc_dic_population_units:
            if not models.EtcDicPopulationUnit.query.filter_by(
                    population_units=unit.population_units,
                    dataset_id=dataset.id).all():
                new_unit = models.EtcDicPopulationUnit(
                    order=unit.order,
                    population_units=unit.population_units,
                    details=unit.details,
                    code=unit.code,
                    dataset_id=dataset.id,
                )
                models.db.session.add(new_unit)
                models.db.session.commit()

        print("Importing EtcDicSpeciesType...")
        etc_dic_species_types = models.EtcDicSpeciesType.query.all()
        for type in etc_dic_species_types:
            if not models.EtcDicSpeciesType.query.filter_by(
                SpeciesTypeID=type.SpeciesTypeID,
                dataset_id=dataset.id
            ):
                new_type = models.EtcDicSpeciesType(
                    SpeciesTypeID=type.SpeciesTypeID,
                    SpeciesType=type.SpeciesType,
                    Assessment=type.Assessment,
                    Note=type.Note,
                    abbrev=type.abbrev,
                    dataset_id=dataset.id
                )
                models.db.session.add(new_type)
                models.db.session.commit()

        print("Importing EtcDicTrend...")
        etc_dic_trends = models.EtcDicTrend.query.all()
        for trend in etc_dic_trends:
            if not models.EtcDicTrend.query.filter_by(
                id=trend.id,
                dataset_id=dataset.id
            ):
                new_trend = models.EtcDicTrend(
                    id=trend.id,
                    trend=trend.trend,
                    details=trend.details,
                    dataset_id=dataset.id,
                )
                models.db.session.add(new_trend)
                models.db.session.commit()

generate_new_period = Manager()
generate_new_period.add_command('run', GenerateNewPeriodCommand())