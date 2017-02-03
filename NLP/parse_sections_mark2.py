# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 18:26:31 2017

@author: leon
"""

import re

def get_sections(filename):
    business_count = 0
    risk_count = 0
    line_count = 0
    business = re.compile('^\w{4,5}\s1\.$')
    risks = re.compile('^\w{4,5}\s1A\.$')
    end_section = re.compile('^\w{4,5}\s1B\.$')
    
    file = open(filename, 'r')
    key = ""
    sections = {}

    for line in file:
        line = line.strip()
        line_count+=1
        if business.match(line):
            business_count+=1
            if business_count == 1:
                key = "Business Overview"
                sections[key] = ""
            else:
                key = "Business Overview"
                sections[key] = ""
        elif risks.match(line):
            risk_count+=1
            if risk_count == 1:
                key = "Risk Factors"
                sections[key] = ""
            else:
                key = "Risk Factors"
                sections[key] = ""
        elif end_section.match(line):
            if line_count > 300:
                break
        else:
            if key != "":
                newline = sections[key] + line
                sections[key] = newline
    return sections



"""
def set_key(sections, key_count, key_value, global_key):
    if key_count == 1:
        global_key = key_value
        sections[global_key] = ""
    else:
        global_key = key_value
        sections[global_key] = ""
    


def get_sections(filename):
    business_count = 0
    risk_count = 0
    line_count = 0
    business = re.compile('^\w{4,5}\s1\.$')
    risks = re.compile('^\w{4,5}\s1A\.$')
    end_section = re.compile('^\w{4,5}\s1B\.$')
    
    file = open(filename, 'r')
    key = ""
    sections = {}

    for line in file:
        line = line.strip()
        line_count+=1
        if business.match(line):
            business_count+=1
            set_key(sections, business_count, "Business Overview", key)
            print(key)
        elif risks.match(line):
            risk_count+=1
            set_key(sections, risk_count, "Risk Factors", key)
            print(key)
        elif end_section.match(line):
            if line_count > 300:
                break
        else:
            if key != "":
                newline = sections[key] + line
                sections[key] = newline
    return sections
"""
sections = get_sections('C:/Users/leon/Desktop/AIF-Risk/10K/CXW_10K_2015.txt')
        
        

        






    