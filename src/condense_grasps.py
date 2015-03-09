import math
import numpy as np
from get_grasp_type import get_wrist_roll


class CondenseGraspTypes():

    def __init__(self, num_condensed_grasp_types=8, num_bins_per_joint=5):
        self.num_condensed_grasp_types = num_condensed_grasp_types
        self.num_bins_per_joint = num_bins_per_joint

    #helper function to determine what bin a data point belongs in.
    def get_bin(self, data_point, bin_edges):
        bin_id = -1
        for bin_edge in bin_edges:

            #this will never pass on first bin_edge
            if data_point < bin_edge:
                break

            bin_id += 1

        #sanity check
        assert bin_id >= 0
        assert bin_id < len(bin_edges) - 1

        return bin_id

    def get_grasp_type(self, bin_values, bin_edges_list, num_entries_per_bin):

        grasp_type = 0

        for i in range(len(bin_values)):

            bin_value = bin_values[i]
            bin_edges = bin_edges_list[i]

            bin_id = self.get_bin(bin_value, bin_edges)

            grasp_type += bin_id * math.pow(num_entries_per_bin, i)

        return grasp_type

    #now we are going to condense the dataset to only include grasps that have a reasonably large number of examples
    #this will remove lots of the labels that do not actually correspond to feasible grasps.
    def condense_grasp_types(self, grasp_types, num_grasp_types):

        # grasp_types_sorted = copy.copy(list(set(grasp_types)))
        # grasp_types_sorted.sort()
        # grasp_types_sorted.reverse()

        counts = np.zeros(num_grasp_types)
        for grasp_type_id in grasp_types:
            counts[grasp_type_id] += 1

        counts_sorted = list(counts)
        counts_sorted.sort()
        counts_sorted.reverse()

        threshold = counts_sorted[self.num_condensed_grasp_types - 1]

        grasp_type_to_condensed_grasp_type = {}
        current_condensed_grasp_id = 0
        for i in range(len(counts)):
            if counts[i] >= threshold:
                grasp_type_to_condensed_grasp_type[i] = current_condensed_grasp_id
                current_condensed_grasp_id += 1

        return grasp_type_to_condensed_grasp_type

    def condense_grasps(self, grasps, grasp_class):

        slop = .01
        bin_ranges = [(0,  math.pi + slop),
                      (0, 2.44 + slop),
                      (0, .84 + slop),
                      (0,  math.pi + slop),
                      (0, 2.44 + slop),
                      (0, .84 + slop),
                      (0, 2.44 + slop),
                      (0, .84 + slop),
                      (-math.pi - slop, math.pi + slop)]

        num_entries_per_bin = self.num_bins_per_joint

        num_grasp_types = math.pow(num_entries_per_bin, len(bin_ranges))


        bin_edges = []
        for bin_range in bin_ranges:
            hist, edges = np.histogram([], num_entries_per_bin, bin_range)
            bin_edges.append(edges)

        count = 0

        grasp_types = []
        print "Iterating through raw grasps"
        for grasp in grasps:

            if count % 500 == 0:
                print str(count) + '/' + str(len(grasps))

            bins = list(grasp.joint_values)
            bins.append(get_wrist_roll(grasp))

            grasp_type = self.get_grasp_type(bins, bin_edges, num_entries_per_bin)
            grasp_types.append(int(grasp_type))

            count += 1

        print "Building grasp type to condensed grasp type dict"
        grasp_type_to_condensed_grasp_type = self.condense_grasp_types(grasp_types, num_grasp_types)

        actual_num_condensed_grasp_types = len(grasp_type_to_condensed_grasp_type.keys())

        condensed_grasps = []
        count = 0
        print "Reducing grasps"
        for grasp in grasps:
            if count % 500 == 0:
                print str(count) + '/' + str(len(grasps))

            bins = list(grasp.joint_values)
            bins.append(get_wrist_roll(grasp))
            grasp_type = self.get_grasp_type(bins, bin_edges, num_entries_per_bin)

            if grasp_type in grasp_type_to_condensed_grasp_type:
                uncondensed_grasp_dict = grasp.__dict__
                uncondensed_grasp_dict['grasp_type'] = grasp_type_to_condensed_grasp_type[grasp_type]
                condensed_grasps.append(grasp_class(**uncondensed_grasp_dict))

            count += 1

        return condensed_grasps