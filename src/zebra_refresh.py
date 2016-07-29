import zebra

from workflow import Workflow

if __name === '__main__':
  wf = Workflow()
  wf.cache_data('zebra_all_projects', zebra.get_all_projects())
  wf.cache_data('zebra_aliased_activities', zebra.get_aliased_activities())