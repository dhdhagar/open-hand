from typing import Any, Collection, List
import pprint

from pymongo.cursor import Cursor

from .data import ClusteringRecord, MentionRecords, papers2dict, signatures2dict

from .mongoconn import dbconn

from .shadowdb_schemas import (
    PaperRec,
    PaperRecSchema,
    SignatureRec,
    SignatureRecSchema,
)


signature_coll = dbconn.signatures
clusters_coll = dbconn.clusters


def get_clusters_for_canopy(canopy: str) -> List[ClusteringRecord]:
    cursor: Cursor = clusters_coll.find({"canopy": canopy})

    cluster_ids: List[str] = [c["cluster_id"] for c in cursor]
    cluster_ids: List[str] = list(set(cluster_ids))
    pprint.pp(cluster_ids)
    clusters = [get_cluster(c) for c in cluster_ids]

    return clusters


def add_all_referenced_signatures(mentions: MentionRecords) -> MentionRecords:
    paperids = [paper_id for (paper_id, _) in mentions.papers.items()]
    all_sigs: List[SignatureRec] = [
        SignatureRecSchema().load(sig) for sig in signature_coll.find({"paper_id": {"$in": paperids}})
    ]
    sigdict = dict([(sig.signature_id, sig) for sig in all_sigs])
    combined_sigdict = mentions.signatures | sigdict
    return MentionRecords(papers=mentions.papers, signatures=combined_sigdict)


def get_canopied_signatures(canopystr: str) -> List[SignatureRec]:
    coll: Collection[Any] = signature_coll.aggregate(
        [
            {"$match": {"author_info.block": {"$eq": canopystr}}},
            {
                "$lookup": {
                    "from": "clusters",
                    "localField": "signature_id",
                    "foreignField": "signature_id",
                    "as": "clusters",
                }
            },
            {"$set": {"cluster": {"$arrayElemAt": ["$clusters", 0]}}},
            {"$set": {"cluster_id": "$cluster.cluster_id"}},
            {"$project": {"_id": 0, "__v": 0, "clusters": 0, "cluster": 0}},
        ]
    )
    signatures: List[SignatureRec] = [SignatureRecSchema().load(p) for p in coll]
    return signatures


def get_canopy(canopystr: str) -> MentionRecords:
    sigs = get_canopied_signatures(canopystr)
    sig_dict = signatures2dict(sigs)

    coll: Collection[Any] = signature_coll.aggregate(
        [
            {"$match": {"author_info.block": {"$eq": canopystr}}},
            {"$project": {"_id": 0, "paper_id": 1}},
            {
                "$lookup": {
                    "from": "paper",
                    "localField": "paper_id",
                    "foreignField": "paper_id",
                    "as": "fromItems",
                }
            },
            {
                "$replaceRoot": {
                    "newRoot": {
                        "$mergeObjects": [
                            {"$arrayElemAt": ["$fromItems", 0]},
                            "$$ROOT",
                        ]
                    }
                }
            },
            {"$project": {"fromItems": 0}},
            {"$project": {"_id": 0, "__v": 0}},
        ]
    )

    papers: List[PaperRec] = [PaperRecSchema().load(p) for p in coll]

    paper_dict = papers2dict(papers)

    return MentionRecords(papers=paper_dict, signatures=sig_dict)


def get_canopy_strs() -> List[str]:
    distinct_canopies = dbconn.command({"distinct": "signatures", "key": "author_info.block"})
    canopies = distinct_canopies["values"]
    return canopies


def get_cluster(clusterstr: str) -> ClusteringRecord:
    coll: Collection[Any] = signature_coll.aggregate(
        [
            {"$match": {"cluster_id": {"$eq": clusterstr}}},
            {"$project": {"_id": 0}},
            {
                "$lookup": {
                    "from": "signatures",
                    "localField": "signature_id",
                    "foreignField": "signature_id",
                    "as": "signatures",
                }
            },
            {
                "$lookup": {
                    "from": "paper",
                    "localField": "signatures.paper_id",
                    "foreignField": "paper_id",
                    "as": "papers",
                }
            },
        ]
    )
    final_cluster = [p for p in coll]

    # paper_canopy_dict = dict(paper_canopy)

    # pprint.pprint(final_cluster)
    papers = [PaperRecSchema().load(rec["papers"][0]) for rec in final_cluster]
    signatures = [SignatureRecSchema().load(rec["signatures"][0]) for rec in final_cluster]
    paperdict = dict([(p.id, p) for p in papers])
    sigdict = dict([(s.signature_id, s) for s in signatures])
    mentions = MentionRecords(papers=paperdict, signatures=sigdict)

    c0 = final_cluster[0]
    cluster_id = c0["cluster_id"]
    prediction_group = c0["id"]
    canopystr = c0["canopy"]

    return ClusteringRecord(
        mentions=mentions, prediction_group=prediction_group, cluster_id=cluster_id, canopy=canopystr
    )
