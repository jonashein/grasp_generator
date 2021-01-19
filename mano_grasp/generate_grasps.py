#!/usr/bin/env python2

import argparse
import json
import os
import time
import numpy as np

from graspit_process import GraspitProcess
from graspit_scene import GraspitScene
from grasp_miner import GraspMiner

parser = argparse.ArgumentParser(description='Grasp mining')
parser.add_argument('-m', '--models', nargs='*', default=['glass'])
parser.add_argument('-l', '--models_file', type=str, default='')
parser.add_argument('-n', '--n_jobs', type=int, default=1)
parser.add_argument('-o', '--path_out', type=str, default='')
parser.add_argument('-v', '--verbose', action='store_true')
parser.add_argument('-d', '--debug', action='store_true')
parser.add_argument('-e', '--headless', action='store_true', help="Start in headless mode")
parser.add_argument('-x',
                    '--xvfb',
                    action='store_true',
                    help="Start with Xserver Virtual Frame Buffer (Xvfb)")
parser.add_argument('--graspit_dir',
                    type=str,
                    default=os.environ['GRASPIT'],
                    help="Path to GraspIt root directory")
parser.add_argument('--grasps_file',
                    type=str,
                    help="Grasps database .txt file")
parser.add_argument('--plugin_dir',
                    type=str,
                    default=os.environ['GRASPIT_PLUGIN_DIR'],
                    help="Path to directory with a graspit_interface plugin")
parser.add_argument('-s', '--max_steps', type=int, default=0, help="Max search steps per object")
parser.add_argument('-g', '--max_grasps', type=int, default=0, help="Max best grasps per object")
parser.add_argument('--relax_fingers',
                    action='store_true',
                    help="Randomize squezzed fingers positions")
parser.add_argument('--change_speed', action='store_true', help="Try several joint's speed ratios")


def loadPredefinedGrasps(grasps_file):
    plans = []

    with open(grasps_file, 'r') as f:
        lines = f.readlines()

    idx = 0
    while idx < len(lines) - 1:
        dofs_raw = lines[idx].replace(",", ".").split(" ")
        dofs_raw.remove("\n")
        pose_raw = lines[idx + 1].replace(",", ".").split(" ")
        pose_raw.remove("\n")

        dofs_type = int(dofs_raw[0])
        pose_type = int(pose_raw[0])
        assert dofs_type == 5, "Wrong dofs type!"  # type 5 is POSE_DOF
        assert pose_type == 0, "Wrong pose type!"  # type 0 is SPACE_COMPLETE, in this case 3D position "X Y Z" followed by orientation as quaternion "w x y z"

        dofs = np.array(dofs_raw[1:], dtype=np.float)
        pose = np.array(pose_raw[1:], dtype=np.float)

        # Pipeline expects pose in format pos.x, pos.y, pos.z, orn.x, orn.y, orn.z, orn.w, so orn.w has to be moved to the back
        # Also, positions have to be converted from millimeters to meters
        pose = np.concatenate((np.array(pose[:3]) / 1000.0, pose[4:], [pose[3]]))
        plans.append({'pose': pose, 'dofs': dofs})
        idx += 2

    # print("plans: {}".format(plans))
    return plans


def main(args):
    if not os.path.isdir(args.graspit_dir):
        print('Wrong GraspIt path: "{}"'.format(args.graspit_dir))
        exit(0)

    if not os.path.isdir(args.plugin_dir):
        print('Wrong plugins path: "{}"'.format(args.plugin_dir))
        exit(0)

    if args.models_file and not os.path.isfile(args.models_file):
        print('File not exists: "{}"'.format(args.models_file))
        exit(0)

    plans = None
    if args.grasps_file:
        if os.path.isfile(args.grasps_file):
            try:
                plans = loadPredefinedGrasps(args.grasps_file)
            except Exception as e:
                print("Error while loading predefined grasps: {}".format(e))
        else:
            print('grasps_file does not exist: "{}"'.format(args.grasps_file))
            exit(0)

    if not args.path_out:
        print('Output directory not specified')
        exit(0)

    if not os.path.isdir(args.path_out):
        os.makedirs(args.path_out)

    if not args.models_file:
        models = args.models
    else:
        with open(args.models_file) as f:
            models = f.readlines()

    proccess = GraspitProcess(graspit_dir=args.graspit_dir,
                              plugin_dir=args.plugin_dir,
                              headless=args.headless,
                              xvfb_run=args.xvfb,
                              verbose=args.verbose)

    generator = GraspMiner(graspit_process=proccess,
                           max_steps=args.max_steps,
                           max_grasps=args.max_grasps,
                           relax_fingers=args.relax_fingers,
                           change_speed=args.change_speed)

    if args.n_jobs > 1:
        from joblib import Parallel, delayed
        grasps = Parallel(n_jobs=args.n_jobs, verbose=50)(delayed(generator)(m) for m in models)
    else:
        grasps = [generator(body, plans, augmentGrasps=True) for body in models]

    for body_name, body_grasps in grasps:
        body_name = os.path.basename(body_name)
        print('{}: saving {} grasps in {}'.format(
            body_name,
            len(body_grasps),
            os.path.join(args.path_out, '{}.json'.format(body_name))
        ))
        with open(os.path.join(args.path_out, '{}.json'.format(body_name)), 'w') as f:
            json.dump(body_grasps, f)

    if args.debug:
        with GraspitProcess(graspit_dir=args.graspit_dir, plugin_dir=args.plugin_dir) as p:
            for body_name, body_grasps in grasps:
                scene = GraspitScene(p.graspit, 'ManoHand', body_name)
                for grasp in body_grasps:
                    scene.grasp(grasp['pose'], grasp['dofs'])
                    time.sleep(3.0)


if __name__ == '__main__':
    main(parser.parse_args())
