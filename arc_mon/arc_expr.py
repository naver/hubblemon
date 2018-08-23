

import common.core
import data_loader.loader_util
from chart.chart_data import chart_data


import arc_mon.arc_view


def arc_dashboard(*cluster_list):
	ret = []
	for cluster in cluster_list:
		cluster_map = arc_mon.arc_view.arc_cluster_map
		if cluster not in cluster_map:
			ret.append(data_loader.loader_util.title_loader('cluster %s not found' % cluster))
			continue

		ret.append(data_loader.loader_util.title_loader(cluster))
		pgs_str_list = cluster_map[cluster]
		for pgs_str in pgs_str_list:
			pgs_id, pgs_path = pgs_str.split('-', 1)
			ldr = common.core.loader(pgs_path, ['cmds_processed'])
			ldr.title_prefix = '[PGS %s] ' % pgs_id
			ret.append(ldr)

	return data_loader.loader_util.serial_loader(ret)

def arc_merge_dashboard(*cluster_list):
	ret = []
	for cluster in cluster_list:
		cluster_map = arc_mon.arc_view.arc_cluster_map
		if cluster not in cluster_map:
			ret.append(data_loader.loader_util.title_loader('cluster %s not found' % cluster))
			continue

		#ret.append(data_loader.loader_util.title_loader(cluster))
		pgs_str_list = cluster_map[cluster]

		pgs_loaders = []
		for pgs_str in pgs_str_list:
			pgs_id, pgs_path = pgs_str.split('-', 1)
			ldr = common.core.loader(pgs_path, ['cmds_processed'])
			pgs_loaders.append(ldr)

		merge_ldr = data_loader.loader_util.merge_loader(pgs_loaders)
		merge_ldr.title_prefix = '[%s] ' % cluster
		ret.append(merge_ldr)

	return data_loader.loader_util.serial_loader(ret)

	
def arc_sum_dashboard(*cluster_list):
	ret = []
	for cluster in cluster_list:
		cluster_map = arc_mon.arc_view.arc_cluster_map
		if cluster not in cluster_map:
			ret.append(data_loader.loader_util.title_loader('cluster %s not found' % cluster))
			continue

		#ret.append(data_loader.loader_util.title_loader(cluster))
		pgs_str_list = cluster_map[cluster]

		pgs_loaders = []
		for pgs_str in pgs_str_list:
			pgs_id, pgs_path = pgs_str.split('-', 1)
			ldr = common.core.loader(pgs_path, ['cmds_processed'])
			pgs_loaders.append(ldr)

		sum_ldr = data_loader.loader_util.sum_loader(pgs_loaders)
		sum_ldr.title_prefix = '[%s] ' % cluster
		ret.append(sum_ldr)

	return data_loader.loader_util.serial_loader(ret)



	
