
import os
import rospkg

from grasp import get_model_grasps
from grasp_dataset import GraspDataset

from choose import choose_from
from date_string import get_date_string
from paths import RAW_GRASPIT_DIR, AGG_GRASPIT_DIR
from condense_grasps import CondenseGraspTypes


class GraspAggregator():

    def __init__(self, graspit_grasps_dir, graspit_agg_dir, grasp_dataset, energy_threshold=-.25, num_condensed_grasp_types=8, num_bins_per_joint=5):
        self.graspit_grasps_dir = graspit_grasps_dir
        self.graspit_agg_dir = graspit_agg_dir
        self.grasp_dataset = grasp_dataset
        self.energy_threshold = energy_threshold

        #used for the grasp condensing steps
        self.num_condensed_grasp_types = num_condensed_grasp_types
        self.num_bins_per_joint = num_bins_per_joint

    def run(self):
        grasps = []
        print "reading grasps from files"
        for model_name in os.listdir(self.graspit_grasps_dir):
            grasps = grasps + get_model_grasps(self.graspit_grasps_dir + model_name,
                                               model_name,
                                               graspClass=self.grasp_dataset.Grasp)

        print "condensing grasps"
        grasp_type_condenser = CondenseGraspTypes(num_condensed_grasp_types=self.num_condensed_grasp_types,
                                                  num_bins_per_joint=self.num_bins_per_joint)
        condensed_grasps = grasp_type_condenser.condense_grasps(grasps, self.grasp_dataset.Grasp)

        print "writing low energy grasps to h5"
        num = 0
        for grasp in condensed_grasps:
            if num % 1000 is 0:
                print "%s / %s" % (num, len(condensed_grasps))

            num += 1

            if grasp.energy < self.energy_threshold:
                self.grasp_dataset.add_grasp(grasp)




if __name__ == "__main__":

    graspit_dir = choose_from(RAW_GRASPIT_DIR)
    graspit_grasps_dir = RAW_GRASPIT_DIR + graspit_dir + '/'

    rospack = rospkg.RosPack()
    DATASET_TEMPLATE_PATH = rospack.get_path('grasp_dataset')

    grasp_dataset = GraspDataset(AGG_GRASPIT_DIR + graspit_dir + "-" + get_date_string() + ".h5",
                                 DATASET_TEMPLATE_PATH + "/dataset_configs/graspit_grasps_dataset.yaml")

    grasp_aggregator = GraspAggregator(graspit_grasps_dir, AGG_GRASPIT_DIR, grasp_dataset)
    grasp_aggregator.run()

    import IPython
    IPython.embed()
    assert False
