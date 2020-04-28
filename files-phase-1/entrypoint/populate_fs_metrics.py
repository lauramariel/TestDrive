import env
from minerva.nvm.nvm_insights_store import NvmInsightsStore
from minerva.server_utils.minerva_utils import *
import time
import random
from collections import defaultdict
import pprint

METRICS_SPEC_LIST = \
[("file_server", "fs_usedbydataset_bytes", 10, 200, (1048576 * 1024 * 100)),
 ("file_server", "fs_usedbysnapshots_bytes", 5, 100, (1048576 * 1024 * 100)),
 ("file_server", "total_space_used_bytes", 15, 210, (1048576 * 1024 * 100)),
 ("file_server", "fs_referenced_bytes", 8, 150, (1048576 * 1024 * 100)),
 ("file_server", "statvfs_f_files",  10000, 1000000, 1),
 ("file_server", "statvfs_f_ffree", 5000, 50000, 1),
 ("file_server", "statvfs_files_used", 5000, 50000, 1),
 ("file_server", "fs_overall_latency", 10, 300, 1000000),
 ("file_server", "fs_write_latency", 3, 100, 1000000),
 ("file_server", "fs_read_latency", 3, 100, 1000000),
 ("file_server", "fs_metadata_latency",3, 100, 1000000),
 ("file_server", "fs_overall_tput",  100, 800, (1024 * 1024)),
 ("file_server", "fs_overall_iops",  10, 30, 1000),
 ("file_server", "fs_write_iops",  5, 10, 1000),
 ("file_server", "fs_write_tput",  30, 250, (1024 * 1024)),
 ("file_server", "total_smb_connections",  10, 1000, 1),
 ("file_server", "fs_read_iops", 5, 10, 1000),
 ("file_server", "fs_read_tput", 30, 250, (1024 * 1024)),
 ("file_server", "fs_metadata_iops", 5, 10, 1000),
 ("file_server", "total_available_space_bytes", 5, 50, (1048576 * 1024 * 100)),
 ("file_server", "fs_used_space_bytes", 15, 210, (1048576 * 1024 * 100))]

SHARE_METRIC_LIST = \
[("file_server_share", "share_usedbydataset_bytes", 10, 200, (1048576 * 1024 * 100)),
 ("file_server_share", "share_usedbysnapshots_bytes", 5, 100, (1048576 * 1024 * 100)),
 ("file_server_share", "share_used_bytes" ,15, 210, (1048576 * 1024 * 100)),
 ("file_server_share", "share_available_bytes", 5, 50, (1048576 * 1024 * 100)),
 ("file_server_share", "share_referenced_bytes", 8, 150, (1048576 * 1024 * 100)),
 ("file_server_share", "share_statvfs_f_files", 10000, 1000000, 1),
 ("file_server_share", "share_statvfs_f_ffree", 5000, 50000, 1),
 ("file_server_share", "share_statvfs_files_used", 5000, 50000, 1),
 ("file_server_share", "share_overall_latency", 10, 300, 1000000),
 ("file_server_share", "share_write_latency", 3, 100, 1000000),
 ("file_server_share", "share_read_latency", 3, 100, 1000000),
 ("file_server_share", "share_metadata_latency",3, 100, 1000000),
 ("file_server_share", "share_overall_tput", 100, 800, (1024 * 1024)),
 ("file_server_share", "share_overall_iops", 10, 30, 1000),
 ("file_server_share", "share_write_iops", 5, 10, 1000),
 ("file_server_share", "share_write_tput", 30, 250, (1024 * 1024)),
 ("file_server_share", "share_smb_connections", 10, 1000, 1),
 ("file_server_share", "share_read_iops", 5, 10, 1000),
 ("file_server_share", "share_read_tput", 30, 250, (1024 * 1024)),
 ("file_server_share", "share_metadata_iops", 5, 10, 1000)]

def populate_metrics(populate_ts, metric_map):
  for metrics in METRICS_SPEC_LIST:
    (entity_name, metric_name, start_val, end_val, mult_factor) = metrics
    val = random.randint(start_val, end_val) * mult_factor
    metric_map[metric_name].append((val, populate_ts))

def populate_share_metrics(populate_ts, share_metric_map):
  for share_metrics in SHARE_METRIC_LIST:
    (entity_name, metric_name, start_val, end_val, mult_factor) = share_metrics
    val = random.randint(start_val, end_val) * mult_factor
    share_metric_map[metric_name].append((val, populate_ts))

num_hours_to_populate = int(sys.argv[1]) or 24
num_samples_per_hour = int(sys.argv[2]) or 12
curr_ts = int(time.time() * 1e6)
nvm_insights_store = NvmInsightsStore()
fs_uuid = nvm_insights_store.get_local_file_server_uuid()
share_info = nvm_insights_store.get_all_share_info()

entity_list = list()
entity_tuple = ("file_server", fs_uuid)
entity_list.append(entity_tuple)
for share_uuid in share_info:
  entity_tuple = ("file_server_share", share_uuid)
  entity_list.append(entity_tuple)

for curr_hour in xrange(num_hours_to_populate):
  curr_ts = curr_ts - int(3600 * curr_hour * 1e6)
  pop_ts = curr_ts
  metric_map = defaultdict(list)
  share_metric_map_list = list()
  for share_uuid in share_info:
    share_metric_map_list.append(defaultdict(list))
  metric_list = list()
  for ii in xrange(num_samples_per_hour):
    pop_ts = pop_ts - int((3600 / num_samples_per_hour) * 1e6)
    #print("pop_ts:%s" % pop_ts)
    populate_metrics(pop_ts, metric_map)
    for (idx, share_uuid) in zip(xrange(len(share_info)), share_info):
      populate_share_metrics(pop_ts, share_metric_map_list[idx])
  metric_list.append(metric_map)
  metric_list.extend(share_metric_map_list)
  #print("Populating fs metrics for %s hour." % curr_hour)
  #pprint.pprint((metric_list))
  MinervaUtils.put_metric_data(entity_list, metric_list)
print("Done populating fs metrics.")
