# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 21:19:46 2017

@author: brendanbailey
"""

import pandas as pd
import requests
import os
import matplotlib.pyplot as plt

def get_robots(site_list):
    error_log = open("error_log.txt", "w")
    for site in site_list:
        try:
            r = requests.get("http://%s/robots.txt" % site)
            f = open("txt_files/%s_robots.txt" % site.replace(".","_"), "w")
            try: #I want to avoid rencoding if possible because I want to make sure robots.txt are properly preserved
                f.write(r.text)
            except UnicodeEncodeError:
                f.write(r.text.encode('ascii', 'ignore'))
                error_log.write(site + "\t Unicode Encode Error Handled \n")
            f.close() 
        except Exception as detail:
            error_log.write(site + "\t" + str(detail) + "\n")
    error_log.close()

def scan_robots_txt(indir):
    robots_dictionary = {}
    for root, dirs, filenames in os.walk(indir):
        for f in filenames:
            if f != ".DS_Store":
                site_name = f
                robots_dictionary[site_name] = {"type": "", "disallow": [], "allow":[]}
                #Checking if there are any generic rules
                robots_file = open(os.path.join(root, f), 'r')
                robot_text = robots_file.read()
                asterisk_count = robot_text.upper().count("USER-AGENT: *")
                if asterisk_count != 1:
                    robots_dictionary[site_name]["type"] = "Not Set"
                else:
                    #Collecting Allows and Disallows
                    data = robot_text.upper().split("USER-AGENT: *")[1].split("USER-AGENT:")[0].split("\n") #Selecting only generic user section
                    error = False
                    for line in data:
                        try:
                            if "DISALLOW:" == line.strip():
                                robots_dictionary[site_name]["disallow"].append("")
                            elif "ALLOW:" == line.strip():
                                robots_dictionary[site_name]["allow"].append("")
                            elif "DISALLOW:" in line.upper():
                                robots_dictionary[site_name]["disallow"].append(line.split(" ")[1])
                            elif "ALLOW:" in line.upper():
                                robots_dictionary[site_name]["allow"].append(line.split(" ")[1])
                        except IndexError:
                            error = True
                    
                    #Categorizing Site
                    if error is True:
                        robots_dictionary[site_name]["type"] = "error"
                    elif robots_dictionary[site_name]["disallow"] == ["/"] and robots_dictionary[site_name]["allow"] == []:
                        robots_dictionary[site_name]["type"] = "Complete Disallow"
                    elif robots_dictionary[site_name]["disallow"] == [""] or robots_dictionary[site_name]["disallow"] == []:
                        robots_dictionary[site_name]["type"] = "Complete Allow"
                    else:
                        robots_dictionary[site_name]["type"] = "Mixed"
                robots_file.close()
        return robots_dictionary

def generate_output(dictionary):
    #Create Dict for Pie Chart and Writing Data to File
    type_dict = {}
    output_file = open("output_file.txt", "w")
    output_file.write("Site\tType\tAllow\tDisallow\n")
    for k in dictionary:
        write_list = [k, dictionary[k]["type"], str(dictionary[k]["allow"]), str(dictionary[k]["disallow"])]
        output_file.write("\t".join(write_list) + "\n")
        try:
            type_dict[dictionary[k]["type"]] += 1
        except KeyError:
            type_dict[dictionary[k]["type"]] = 1
    output_file.close()
        
    #Create Pie Save Pie Chart
    fig1, ax1 = plt.subplots()
    ax1.pie(type_dict.values(), labels=type_dict.keys(), explode = (0,0.2, 0.2, 0.2), colors = ("#6973f0", "#c62929", "#fcce25", "#0cca00"), autopct='%1.0f%%', shadow=True, startangle=45)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.style.use('ggplot')
    plt.title("Robots.txt Rules of Most Popular Sites", fontweight = "bold")
    plt.savefig('pie_chart.png')
    
#Already got data, so I'm commenting these out
#site_df = pd.read_csv("wikipedia_popular_sites.csv")
#sites = list(site_df.Domain)
#get_robots(sites)

robots_dictionary = scan_robots_txt('./txt_files')
#Taobao.com has to be special by including two spaces in between their colons. The code above doesn't handle for this, so correcting through hard coding.
robots_dictionary['taobao_com_robots.txt']["type"] = "Complete Disallow"
robots_dictionary['taobao_com_robots.txt']["disallow"] = ["/"]

#I did not account for YouTube and WhatsApp's https protocols above. Correcting for them here for final analysis.
robots_dictionary['youtube_com_robots.txt']["type"] = "Mixed"
robots_dictionary['youtube_com_robots.txt']["disallow"] = ["Error in Data Collection"]
robots_dictionary['youtube_com_robots.txt']["allow"] = ["Error in Data Collection"]
robots_dictionary['whatsapp_com_robots.txt']["type"] = "Mixed"
robots_dictionary['whatsapp_com_robots.txt']["disallow"] = ["Error in Data Collection"]
robots_dictionary['whatsapp_com_robots.txt']["allow"] = ["Error in Data Collection"]

generate_output(robots_dictionary)
