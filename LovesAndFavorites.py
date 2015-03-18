""" Analyze the favorites, loves, views, comments of Scratchers
  
  Author: csp@google.com
  Late updated: 3/16/15 """

import json, requests, time, logging as log, argparse
from bs4 import BeautifulSoup

def get_project_ids_from_scratch(user):
  """ Gets all project IDs for a given Scratch user
    
    Args:
    A username of a Scratch user
    
    Returns:
    A list of project ids
    """
  url = 'http://scratch.mit.edu/users/%s/projects/' % user
  r = requests.get(url)
  soup = BeautifulSoup(r.text)
  ids = []

  for link in soup.find_all('a'):
    link = link.get('href')
    if link:
        if 'projects' in link and 'editor' not in link:
            link = link.split("/")
            ids.append(link[2])
                                                    
  ids = set(ids)
  return ids

def initialize_outfile():
  with open('workfile2.txt', 'w') as out:
    firstline = ("user, project, favorites, loves, views, comments, title, "
                 "description, datetime_shared, timestamp_analyzed\n")
    out.write(firstline)

def write_to_outfile(user, id, project_data, comments):
  """ Write the results of analyzing 1 project to the outfile
    
    Args:
    A username of a Scratcher, the ID of a project, a list of JSON project data 
    from Scratch 2.0 API, a string representing the number of comments """
  with open('workfile2.txt', 'a') as out:
    
    text = user + "," + id + ","
    
    # If the Scratch request failed, write N/A
    if project_data == "N/A":
      log.debug("Found N/A project data")
      out.write(text + "\n")
      log.info("project written: %s" % id)

    # If the Scratch request succeeded
    else:
      # Try writing the analysis to the outfile
      try:
        description = " ".join(project_data['description'].splitlines())
        
        # Replace characters that can't be escaped in Spreadsheets easily
        description = description.replace(",",";")
        description = description.replace("(",";")
        description = description.replace(")",";")
        description = description.replace('"',";")
        
        text2 = (text, ",".join([project_data['favorite_count'],
                                 project_data['love_count'],
                                 project_data['view_count'], comments,
                                 project_data['title'], description,
                                 project_data['datetime_shared']]
                                ), ",", str(time.time()), "\n")
        text2 = "".join(text2)
        out.write(text2)
        log.info("project written: %s" % id)
      # Exceptions for errors that have non-ascii characters
      except UnicodeError, TypeError:
        out.write(text + "\n")

    # Delay for the next request, so as not to be blocked by Scratch servers
    time.sleep(2)
        
  out.close()

def get_json_for_project(id):
  """ Get the JSON representation of a single project, using Scratch 2.0 API
    
    Args:
    The ID of a Scratch project
    
    Returns:
    A dictionary with JSON data, or string "N/A" if request fails
    """
  
  # Build the URL for the request
  url = "http://scratch.mit.edu/api/v1/project/" + id + "/?format=json"
  
  # Send request to Scratch 2.0 API
  r = requests.get(url)
  
  # Try decoding the JSON result
  try:
    decoded = json.loads(r.text)
  
  # JSON cannot be decoded, return a string "N/A"
  except ValueError:
    return "N/A"

  return decoded

def get_comment_count(id):
  """ Get the number of comments for a Scratch project
    
    Args:
    The ID of a Scratch project
    
    Returns:
    A string representing the number of comments on the project
    """
  r = requests.get("http://scratch.mit.edu/projects/%s/" % id)
  soup = BeautifulSoup(r.text)
  
  # Find all div elements
  for item in soup.find_all("div", class_="box-head"):
    for string in item.strings:

      # Find div element used for Comments
      if 'Comments' in string:
        
        # Split out the irrelevant information
        return string.split("(")[1].split(")")[0]
      else:
        return "0"

def get_data_for_user(user):
  """ Helper function to analyze a single user
    
    Args:
    The ID of a Scratcher
    """
  log.info("user started: %s" % user)

  ids = get_project_ids_from_scratch(user)

  # For each project, get the JSON data from Scratch API and
  # the number of comments from a direct request to Scratch.
  # Then write data to an outfile
  for id in ids:
    project_data = get_json_for_project(id)
    comments = get_comment_count(id)
    write_to_outfile(user, id, project_data, comments)
  

  log.info("user completed")

def main():
  
  # set up parser to accept "verbose" and "debug" arguments
  parser = argparse.ArgumentParser()
  parser.add_argument("--verbose", help="increase output verbosity",
                      action="store_true")
  parser.add_argument("--debug", help="increase output verbosity for debugging",
                      action="store_true")
  args = parser.parse_args()
  
  # set logging to handle "verbose" and "debug" arguments
  if args.verbose:
    log.getLogger("requests").setLevel(log.WARNING)
    log.basicConfig(format="%(levelname)s: %(message)s", level=log.INFO)
    log.info("Verbose output.")
  if args.debug:
    log.getLogger("requests").setLevel(log.WARNING)
    log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
    log.info("Verbose output.")
  else:
    log.basicConfig(format="%(levelname)s: %(message)s")

  # create the outfile for the data
  initialize_outfile()

  # users to analyze
  users = ('csf30523','csf30524','csf30525','csf30526','csf30527','csf30528','csf30533','csf30545','csf30546','csf30548','csf30557','csf30565','csf33028','csf24235','csf24236','csf24241','csf24248','csf24251','csf24323','csf24324','csf24330','csf24436','csf24440','csf24441','csf24442','csf24443','csf24444','csf24445','csf24446','csf24451','csf24453','csf36976','csf36978','csf36981','csf36984','csf37049','csf23643','csf23648','csf23650','csf23760','csf23763','csf24286','csf28465','csf15927','csf15905','csf15890','csf15933','csf1503','csf15910','csf15900','csf15897','csf15917','csf15899','csf15951','csf15941','csf15922','csf16067','csf15457','csf15430','csf15470','csf15433','csf15444','csf15445','csf15432','csf16971','csf15475','csf15442','csf15447','csf15450','csf15452','csf15439','csf15472','csf15434','csf15465','csf15455','csf15460','csf16975','csf15440','csf15468','csf15446','csf15463','csf15461','csf15464','csf15441','csf15479','csf15482','csf15466','csf15201','csf15171','csf34613','csf15176','csf15214','csf15179','csf15174','csf15192','csf15219','csf15209','csf15188','csf15198','csf15202','csf15180','csf15211','csf15193','csf15177','csf15200','csf15226','csf15224','csf15227','csf15217','csf15203','csf15205','csf15210','csf35418','csf34526','csf15022','csf14975','csf15035','csf15041','csf15021','csf15020','csf14978','csf14976','csf14973','csf15051','csf14992','csf14994','csf14983','csf15034','csf15013','csf15030','csf15042','csf15008','csf34530','csf15050','csf15073','csf14995','csf14974','csf14987','csf15011','csf14990','csf15019','csf15028','csf15047','csf16553','csf14981','csf15023','csf16544','csf15029','csf15026','csf24184','csf24185','csf24186','csf24187','csf24188','csf24189','csf24191','csf30691','csf30692','csf44476','csf34772','csf42455','csf42599','csf42605','csf42611','csf42612','csf42614','csf42616','csf42618','csf44391','csf44393','csf44394','csf44480','csf44483','csf42663','csf42666','csf42670','csf42672','csf42679','csf42682','csf42683','csf42757','csf42794','csf2778','csf42909','csf42916','csf42918','csf42922','csf42924','csf2936','csf43055','csf43063','csf43064','csf43070','csf43093','csf43105','csf40804','csf40805','csf40809','csf40810','csf40811','csf40812','csf40815','csf40816','csf40817','csf40818','csf40822','csf40823','csf44246','csf41386','csf41309','csf41310','csf41311','csf41313','csf41314','csf41315','csf41316','csf41317','csf31126','csf41321','csf41323','csf41326','csf41327','csf41328','csf41329','csf41330','csf41385','csf41386','csf41388','csf41389','csf41390','csf41392','csf41395','csf41397','csf41398','csf43656','csf31116','csf41396','csf40811','csf41394','csf41396','csf41399','csf41398','csf41385','csf41386','csf41388','csf41392','csf41395','csf41390','csf41389','csf34680','csf27077','csf27080','csf27082','csf27089','csf27090','csf27091','csf27093','csf27096','csf27097','csf27100','csf30895','csf30896','csf26932','csf34880','csf40717','csf42999','csf35859','csf35860','csf35861','csf35862','csf35863','csf35865','csf35866','csf35868','csf35869','csf35870','csf35871','csf35872','csf35874','csf35877','csf35878','csf35882','csf35883','csf35885','csf35886','csf35887')
  # analyze one user at a time
  for user in users:
    get_data_for_user(user)

if __name__ == '__main__':
  main()


