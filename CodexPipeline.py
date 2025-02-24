#!/usr/bin/env python

import argparse
import codex_pipeline
import os
import sys

import sqlite3

POINTING_DB = 'AttitudePointing.db'

def initialize_workspace():
    codex_pipeline.dump_parameters()


    os.makedirs("Input_L2", exist_ok=True)
    os.makedirs("Output_L2", exist_ok=True)

    codex_pipeline.create_db(POINTING_DB)

def update_attitude_db(db_file):

    codex_pipeline.update_db(POINTING_DB, db_file)

    pass


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="CODEX Data Pipeline Master")

    parser.add_argument("--init", action="store_true", help="Initialized to workspace")
    parser.add_argument("--update-attitude", type=str, help="Database to pointing system telemetry")
    
    args = parser.parse_args()


    if( args.init ):
        initialize_workspace()
        sys.exit(0)

    if( args.update_attitude ):
        print(f"Update pointing system telemetry database. {args.update_attitude}")

        update_attitude_db(args.update_attitude)





    