
import unittest
import rospkg
import os

from grasp_dataset import GraspDataset
from paths import TEST_RAW_GRASPIT_DIR, TEST_AGG_GRASPIT_DIR

from aggregate_grasps import GraspAggregator


class TestAggregateGrasps(unittest.TestCase):

    def setUp(self):

        graspit_dir = "contact_and_potential_grasps"
        graspit_grasps_dir = TEST_RAW_GRASPIT_DIR + graspit_dir + '/'

        rospack = rospkg.RosPack()
        DATASET_TEMPLATE_PATH = rospack.get_path('grasp_dataset')

        self.output_file = TEST_AGG_GRASPIT_DIR + graspit_dir + ".h5"

        if os.path.exists(self.output_file):
            os.remove(self.output_file)

        grasp_dataset = GraspDataset(self.output_file ,
                                     DATASET_TEMPLATE_PATH + "/dataset_configs/graspit_grasps_dataset.yaml")

        energy_threshold = -0.25
        self.grasp_aggregator = GraspAggregator(graspit_grasps_dir, TEST_AGG_GRASPIT_DIR, grasp_dataset, energy_threshold)

    def test_output_dim(self):
        self.grasp_aggregator.run()
        self.assertEqual(self.grasp_aggregator.grasp_dataset.get_current_index(), 1662)

    def tearDown(self):
        if os.path.exists(self.output_file):
            os.remove(self.output_file)



if __name__ == '__main__':
    unittest.main()