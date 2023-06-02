"""
@author: Arno
@created: 2023-05-29
@modified: 2023-06-02

Dynamically search for SiteModel

"""
import logging

from src.models.exchange import *
from src.models.info import *
from src.models.sitemodel import SiteModel
from src.models.wallet import *

log = logging.getLogger(__name__)


def inheritors(klass):
    subclasses = set()
    work = [klass]
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                subclasses.add(child)
                work.append(child)
    return subclasses


def find_all_sitemodelsOld() -> set[SiteModel]:
    sitemodel_classnames = inheritors(SiteModel)
    log.debug(f"Get all Site Models: {sitemodel_classnames}")

    sitemodels = set()
    for classname in sitemodel_classnames:
        sitemodels.add(classname())

    return sitemodels


def find_all_sitemodels() -> dict[int, SiteModel]:
    sitemodel_classnames = inheritors(SiteModel)
    log.debug(f"Get all Site Models: {sitemodel_classnames}")

    sitemodels = {}
    for classname in sitemodel_classnames:
        sitemodel: SiteModel = classname()
        sitemodels[sitemodel.site.id] = sitemodel

    return sitemodels
