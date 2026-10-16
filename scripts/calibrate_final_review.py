"""Read real human ratings from a selected review file; no automatic reviewer fabrication."""
import argparse
import json
from pathlib import Path
from capstone_agent.evaluation.calibration import calibrate
ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('run_dir',type=Path);parser.add_argument('--review',required=True,type=Path);args=parser.parse_args()
    protocol=json.loads((ROOT/'evaluation/phase9/protocol_v1.json').read_text())
    judgments=[json.loads(line) for line in (args.run_dir/'judgments_calibration.jsonl').read_text().splitlines()]
    report=calibrate(judgments,json.loads(args.review.read_text()),expected_ids=protocol['human_review_ids'])
    (args.run_dir/'human_calibration.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({key:value for key,value in report.items() if key!='disagreements'},indent=2))

if __name__=='__main__':main()
