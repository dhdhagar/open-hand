from itertools import groupby
from typing import Callable, Dict, List, Optional, Tuple, Union

from s2and.model import Clusterer
from lib.cli_utils import dim, yellowB

from lib.data import (
    AuthorRec,
    ClusteringRecord,
    MentionRecords,
    PaperWithSignatures,
    SignatureRec,
    SignatureWithFocus,
    get_paper_with_signatures,
    papers2dict,
    signatures2dict,
)
from lib.database import add_all_referenced_signatures
from lib.mongoconn import dbconn
from lib.log import logger
from lib.model import load_model
from lib.canopies import get_canopy, get_canopy_strs
from s2and.data import ANDData
from lib.s2and_data import DataPreloads, preload_data

import click

from lib.typedefs import ClusterID, NameCountDict, NameEquivalenceSet


def choose_canopy(n: int) -> str:
    return get_canopy_strs()[n]


def init_canopy_data(mentions: MentionRecords, pre: DataPreloads):
    signature_dict = mentions.signature_dict()
    paper_dict = mentions.paper_dict()
    name_counts: Union[NameCountDict, bool] = pre.name_counts if pre.name_counts is not None else False
    name_tuples: NameEquivalenceSet = pre.name_tuples if pre.name_tuples is not None else set()
    anddata = ANDData(
        signatures=signature_dict,
        papers=paper_dict,
        name="unnamed",
        mode="inference",  # or 'train'
        block_type="s2",  # or 'original', refers to canopy method 's2' => author_info.block is canopy
        name_tuples=name_tuples,
        load_name_counts=name_counts,
    )
    return anddata


def format_authors(authors: List[AuthorRec], fn: Callable[[AuthorRec, int], str]) -> List[str]:
    return [fn(a, i) for i, a in enumerate(authors)]


def format_sig(sig: SignatureWithFocus) -> str:
    if sig.has_focus:
        return yellowB(f"{sig.signature.author_info.fullname}")
    return dim(f"{sig.signature.author_info.fullname}")


def predict_all(*, commit: bool = True, profile: bool = False):
    model = load_model()
    pre = preload_data(use_name_counts=False, use_name_tuples=True)
    canopies = get_canopy_strs()
    for canopy in canopies:
        dopredict(canopy, commit=commit, model=model, pre=pre, profile=profile)


import cProfile, pstats



def dopredict(
    canopy: str, *, commit: bool = False, model: Optional[Clusterer] = None, pre: DataPreloads, profile: bool = False
) -> List[ClusteringRecord]:
    logger.info(f"Clustering canopy '{canopy}', commit = {commit}, profiling={profile}")

    profiler = cProfile.Profile()
    if profile:
        profiler.enable()

    mentions = get_canopy(canopy)
    pcount = len(mentions.papers)
    scount = len(mentions.signatures)
    logger.info(f"Mention counts papers={pcount} / signatures={scount}")

    andData = init_canopy_data(mentions, pre)

    if model is None:
        model = load_model()

    (clustered_signatures, _) = model.predict(andData.get_blocks(), andData)
    cluster_records: List[ClusteringRecord] = []

    for cluster_id, sigids in clustered_signatures.items():
        sigs = [mentions.signatures[sigid] for sigid in sigids]
        papers = [mentions.papers[sig.paper_id] for sig in sigs]
        rec = ClusteringRecord(
            cluster_id=cluster_id,
            prediction_group="p.1",
            canopy=canopy,
            mentions=MentionRecords(signatures=signatures2dict(sigs), papers=papers2dict(papers)),
        )
        cluster_records.append(rec)

    if commit:
        logger.info(f"Committing {len(cluster_records)} clusters for {canopy}")
        commit_clusters(cluster_records)

    if profile:
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats("tottime")
        cname = canopy.replace(" ", "_")
        stats_file = f"canopy_{cname}_n{scount}.prof"
        logger.info(f"Writing stats to {stats_file}")
        stats.dump_stats(stats_file)

    return cluster_records


def commit_cluster(cluster: ClusteringRecord):
    cluster_members = [
        dict(
            prediction_group=cluster.prediction_group,
            cluster_id=cluster.cluster_id,
            signature_id=sigid,
            canopy=cluster.canopy,
        )
        for sigid, _ in cluster.mentions.signatures.items()
    ]
    dbconn.clusters.insert_many(cluster_members)


def commit_clusters(clusters: List[ClusteringRecord]):
    for c in clusters:
        commit_cluster(c)


def mentions_to_displayables(
    mentions_init: MentionRecords,
) -> Tuple[MentionRecords, Dict[ClusterID, List[PaperWithSignatures]]]:
    def keyfn(s: SignatureRec):
        if s.cluster_id is None:
            return "<unclustered>"
        return s.cluster_id

    cluster_groups: Dict[str, List[SignatureRec]] = dict(
        [(k, list(grp)) for k, grp in groupby(mentions_init.signatures.values(), keyfn)]
    )

    cluster_ids = list(cluster_groups)

    mentions = add_all_referenced_signatures(mentions_init)
    cluster_tuples: List[Tuple[ClusterID, List[PaperWithSignatures]]] = []
    for id in cluster_ids:
        sig_zip_papers = [get_paper_with_signatures(mentions, sig) for sig in cluster_groups[id]]
        cluster_tuples.append((ClusterID(id), sig_zip_papers))

    cluster_dict = dict(cluster_tuples)

    return (mentions, cluster_dict)


def displayMentions(mentions_init: MentionRecords):
    _, cluster_dict = mentions_to_displayables(mentions_init)

    cluster_ids = list(cluster_dict)
    for cluster_id in cluster_ids:
        click.echo(f"Cluster is: {cluster_id}")
        cluster = cluster_dict[cluster_id]
        for pws in cluster:
            paper = pws.paper
            title = click.style(paper.title, fg="blue")
            fmtsigs = [format_sig(sig) for sig in pws.signatures]
            auths = ", ".join(fmtsigs)
            click.echo(f"   {title}")
            click.echo(f"      {auths}")

        click.echo("\n")
