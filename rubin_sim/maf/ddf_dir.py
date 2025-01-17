#!/usr/bin/env python

import matplotlib

matplotlib.use("Agg")
import os
import glob
import shutil
import rubin_sim.maf.batches as batches
import rubin_sim.maf.db as db
import rubin_sim.maf.metric_bundles as mb
import argparse


def ddf_dir():
    """
    Run the glance batch on all .db files in a directory.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=str, default=None)
    parser.add_argument("--nside", type=int, default=512)
    args = parser.parse_args()

    if args.db is None:
        db_files = glob.glob("*.db")
        db_files = [filename for filename in db_files if "trackingDb" not in filename]
    else:
        db_files = [args.db]
    run_names = [os.path.basename(name).replace(".db", "") for name in db_files]

    for filename, name in zip(db_files, run_names):
        if os.path.isdir(name + "_ddf"):
            shutil.rmtree(name + "_ddf")
        colmap = batches.col_map_dict()

        bdict = {}
        bdict.update(batches.ddfBatch(run_name=name, nside=args.nside))
        results_db = db.ResultsDb(out_dir=name + "_ddf")
        group = mb.MetricBundleGroup(
            bdict,
            filename,
            out_dir=name + "_ddf",
            results_db=results_db,
            save_early=False,
        )
        group.run_all(clear_memory=True, plot_now=True)
        results_db.close()
        db.add_run_to_database(
            name + "_ddf", "trackingDb_sqlite.db", None, name, "", "", name + ".db"
        )
