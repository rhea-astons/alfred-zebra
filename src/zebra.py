#!/usr/bin/python
# encoding: utf-8

import sys

from workflow import Workflow, web, MATCH_SUBSTRING, MATCH_STARTSWITH
from workflow.background import run_in_background

import helpers, configuration


GITHUB_SLUG = 'rsnts/alfred-zebra'


def CallAPI(endpoint):
  url = config['api_url'] + endpoint
  params = {
    'token': config['api_token']
  }
  r = web.get(url, params=params)
  if r.status_code == 200:
    return r.json()['data']


def get_all_projects():
  return CallAPI('projects')


def get_aliased_activities():
  activities = []
  projects = wf.cached_data('zebra_aliased_activities',
                            get_all_projects,
                            max_age=3600)
  for project in projects:
    for activity in project['activities']:
      if activity['alias']:
        activity['project'] = {
          'id': project['id'],
          'name': project['name']
        }
        activities.append(activity)
  return activities


def filter_all_projects(wf, query):
  projects = wf.cached_data('zebra_all_projects',
                            get_all_projects,
                            max_age=3600)
  query_filter = query.split()
  if len(query_filter) > 1:
    filtered = wf.filter(query_filter[1], projects,
                          key=helpers.search_key_for_project,
                          match_on=MATCH_SUBSTRING)
    if len(query_filter) > 2:
      for i in xrange(2, len(query_filter)):
        filtered = wf.filter(query_filter[i], filtered,
                              key=helpers.search_key_for_project,
                              match_on=MATCH_SUBSTRING)
    return filtered
  return projects


def filter_aliased_activities(wf, query):
  activities = wf.cached_data('zebra_aliased_activities',
                              get_aliased_activities,
                              max_age=3600)
  query_filter = query.split()
  if len(query_filter) > 1:
    filtered = wf.filter(query_filter[1], activities,
                            key=helpers.search_key_for_aliased_activities,
                            match_on=MATCH_SUBSTRING)
    if len(query_filter) > 2:
      for i in xrange(2, len(query_filter)):
        filtered = wf.filter(query_filter[i], filtered,
                              key=helpers.search_key_for_aliased_activities,
                              match_on=MATCH_SUBSTRING)
    return filtered
  return activities


def main(wf):
  import zebra_actions

  query = wf.args[0] if len(wf.args) else None

  if not(config):
    wf.add_item('Configuration missing or incomplete',
                'Please check your configuration file',
                valid=False)
  else:
    if wf.update_available:
      wf.add_item('An update is available!',
                  autocomplete='workflow:update',
                  valid=False,
                  icon=helpers.get_icon(wf, 'cloud-download'))

    if query and query.startswith('project'):
      for project in filter_all_projects(wf, query):
        title = u'{} ({})'.format(project['name'], project['id'])
        autocomplete = u'project {}'.format(project['name'])
        url = config['web_url'] + 'project/' + project['id']
        wf.add_item(title, project['description'],
                    uid=project['id'],
                    arg=url,
                    valid=True,
                    icon=helpers.get_icon(wf, 'project'))
    elif query and query.startswith('alias'):
      for activity in filter_aliased_activities(wf, query):
        title = u'{} [{}]'.format(activity['name'], activity['alias'])
        description = u'Project: {}'.format(activity['project']['name'])
        url = config['web_url'] + 'project/' + activity['project']['id']
        wf.add_item(title, description,
                    uid=activity['alias'],
                    arg=url,
                    valid=True,
                    icon=helpers.get_icon(wf, 'activity'))
    else:
      actions = zebra_actions.ACTIONS

      if query:
        actions = wf.filter(query, actions,
                            key=helpers.search_key_for_action,
                            match_on=MATCH_SUBSTRING)

      if len(actions) > 0:
        for action in actions:
          wf.add_item(action['name'], action['description'],
                      uid=action['name'],
                      autocomplete=action['autocomplete'],
                      arg=action['arg'],
                      valid=action['valid'],
                      icon=helpers.get_icon(wf, 'chevron-right'))

  wf.send_feedback()

  cmd = ['/usr/bin/python', wf.workflowfile('zebra_refresh.py')]
  run_in_background('zebra_refresh', cmd)

if __name__ == '__main__':
  config = configuration.LoadConfig()
  wf = Workflow(update_settings={'github_slug': GITHUB_SLUG})
  sys.exit(wf.run(main))