from lib.facets.authorship import  createCatalogGroupForCanopy
from lib.predef.log import logger

from typing import List, Optional
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    # request, url_for, flash, g, redirect,
)
from lib.shadowdb.data import MentionRecords

from lib.shadowdb.shadowdb import getShadowDB

import math


bp = Blueprint("app", __name__, template_folder="templates")

from flask import render_template


@bp.route("/")
def index():
    logger.debug(f"index:         {url_for('.index')}")
    logger.debug(f"show_canopies: {url_for('.show_canopies')}")
    return redirect(url_for(".show_canopies"))


def author_name_variants(canopy: MentionRecords) -> List[str]:
    variants: List[str] = []

    for _, sig in canopy.signatures.items():
        paper = canopy.papers[sig.paper_id]
        for author in paper.authors:
            if author.position == sig.author_info.position:
                variants.append(author.author_name)

    return list(set(variants))


@bp.route("/canopies")
@bp.route("/canopies/<int:page>")
def show_canopies(page: Optional[int] = None):
    if page is None:
        page = 0

    pagesize = 80
    offset = page * pagesize

    canopystrs = getShadowDB().get_canopy_strs()

    pagecount = math.ceil(len(canopystrs) / pagesize)

    canopypage = canopystrs[offset : offset + pagesize]
    canopies = [(i, cstr, getShadowDB().get_canopy(cstr)) for i, cstr in enumerate(canopypage)]
    counted_canopies = [
        (i, len(mentions.papers), cstr, author_name_variants(mentions)) for i, cstr, mentions in canopies
    ]
    counted_canopies.sort(reverse=True, key=lambda r: r[1])

    return render_template(
        "canopies.html", canopies=counted_canopies, pagecount=pagecount, offset=offset, pagesize=pagesize, page=page
    )


import cProfile, pstats

@bp.route("/canopy/<string:canopy>")
def show_canopy(canopy: str):
    profile = False
    profiler = cProfile.Profile()
    if profile:
        profiler.enable()

    catalog_group = createCatalogGroupForCanopy(canopy)

    if profile:
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats("tottime")
        cname = canopy.replace(" ", "_")
        stats_file = f"canopy_{cname}.prof"
        logger.info(f"Writing stats to {stats_file}")
        stats.dump_stats(stats_file)
    return render_template("canopy.html", canopy=canopy, catalog_group=catalog_group)


@bp.route("/clusters")
def show_clusters():
    return render_template("canopies.html")


@bp.route("/cluster/<string:id>")
def show_cluster(id: str):
    # mentions = getShadowDB().get_canopy(id)
    # papers, signatures = mentions.papers, mentions.signatures
    return render_template("cluster.html")
