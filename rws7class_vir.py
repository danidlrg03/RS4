# -*- coding: utf-8 -*-
"""
Created on Tue Sep 28 12:19:00 2021

@author: sejeand4
"""
import requests
import urllib3
import time
import json

class rws7:
    def __init__(self,ip = '192.168.9.155'):
        urllib3.disable_warnings()
        self.ip = ip
        self.s = requests.Session()
        self.s.auth = ('Default User','robotics')

    #
    # GETEXECSTAT : Retrieve execution state of robot controller
    #    
    def getexecstat(self):
        try:
            r1=self.s.get(f'https://{self.ip}:80/rw/rapid/execution', headers={
                'Accept': 'application/hal+json;v=2.0',
                'Authorization': 'Basic'
                },
                verify=False)
            data = json.loads(r1.content)
            return data['state'][0]['ctrlexecstate']
        except Exception as e:
            print(f"Caught exception {e}")
            return None

    #
    # REQMAST : Requests mastership of robot controller
    #    
    def reqmast(self):
        # payload={}
        headers = {
          'Content-Type': 'application/x-www-form-urlencoded;v=2.0',
          'Authorization': 'Basic'
        }
        try:
            response = self.s.post(f"https://{self.ip}:80/rw/mastership/request",headers=headers,verify = False)
            return  response      
        except Exception as e:
            print(f"Caught exception {e}")
            return None

    #
    # RELMAST : Releases mastership of robot controller
    #    
    def relmast(self):
        url = f"https://{self.ip}:80/rw/mastership/release"
        payload={}
        headers = {
          'Content-Type': 'application/x-www-form-urlencoded;v=2.0',
          'Authorization': 'Basic'
        }
        try:
            response = self.s.post(url, headers=headers, data=payload,verify = False)
            return  response      
        except Exception as e:
            print(f"Caught exception {e}")
            return None
        
    #
    # GETSYMVAL : Reads rapid variable
    #    
    def getsymval(self,task='T_ROB1',module='MainModule',sym='dt_start'):
        url = f"https://{self.ip}:80/rw/rapid/symbol/RAPID/{task}/{module}/{sym}/data"
        payload={}
        headers = {
          'Accept': 'application/hal+json;v=2.0',
          'Authorization': 'Basic'
        }
        try:
            response = self.s.get(url, headers=headers, data=payload,verify = False)
            data = json.loads(response.content)
            return data['state'][0]['value']
        except Exception as e:
            print(f"Caught exception {e}")
            return None

    
    #
    # SETSYMVAL : Sets rapid variable
    #    
    # If to set a string i.e. "sync" use "\"sync\""
    #
    def setsymval(self,task='T_ROB1',module='PowCube',sym='ax5utst',setval = 45.3):
        url = f"https://{self.ip}:80/rw/rapid/symbol/RAPID/{task}/{module}/{sym}/data"
        payload = f"value={setval}"
        print(payload)
        headers = {
          'Content-Type': 'application/x-www-form-urlencoded;v=2.0',
          'Authorization': 'Basic'
        }
        try:
            response = self.s.post(url, headers=headers, data=payload,verify = False)
            return response.text
        except Exception as e:
            print(f"Caught exception {e}")
            return None
    
    #
    # START : Starts execution of rapid program
    #
    def start(self):
        url = f"https://{self.ip}:80/rw/rapid/execution/start?mastership=explicit&action=start"
        payload='regain=continue&execmode=continue&cycle=forever&condition=callchain&stopatbp=disabled&alltaskbytsp=false'
        headers = {
          'Content-Type': 'application/x-www-form-urlencoded;v=2.0',
          'Accept': 'application/json',
          'Authorization': 'Basic'
        }
        try:
            response = self.s.post(url, headers=headers, data=payload,verify = False)
            return response.text
        except Exception as e:
            print(f"Caught exception {e}")
            return None

    #
    # STOP : Stops execution of rapid program
    #
    def stop(self):
        url = f"https://{self.ip}:80/rw/rapid/execution/stop"
        payload = ""
        headers = {
          'Content-Type': 'application/x-www-form-urlencoded;v=2.0',
          'Authorization': 'Basic'
        }
        try:
            response = self.s.post(url, headers=headers, data=payload,verify = False)
            return response.text
        except Exception as e:
            print(f"Caught exception {e}")
            return None

    #
    # PP2MAIN : Puts rapid pointer to beginning of main function
    #
    def pp2main(self):
        url = f"https://{self.ip}:80/rw/rapid/execution/resetpp?mastership=implicit"
        payload={}
        headers = {
          'Accept': 'application/json',
          'Content-Type': 'application/x-www-form-urlencoded;v=2.0',
          'Authorization': 'Basic'
        }
        try:
            response = self.s.post(url, headers=headers, data=payload,verify = False)
            return response.text
        except Exception as e:
            print(f"Caught exception {e}")
            return None

    #
    # READFILE : Reads textfile from controler root dir
    #
    def readfile(self,name='test.txt'):
        url = f"https://{self.ip}:80/fileservice/$home/{name}"
        payload={}
        headers = {'Authorization': 'Basic'}
        try:
            response = self.s.get(url, headers=headers, data=payload, verify = False)
            print(response.text)
        except Exception as e:
            print(f"Caught exception {e}")
            return None

    #
    # PUTFILE : Creates textfile on controler root dir
    #
    def putfile(self,name='test.txt',content = "Hello world!"):
        url = f"https://{self.ip}:80/fileservice/$home/{name}"
        # nl = "\n"
        # mvs = '{'
        # mve = '}'
        # payload = f'{mvs}{nl}     File-content: {content} {nl}{mve}'
        payload = f'{content}'
        headers = {
          'Content-Type': 'application/octet-stream;v=2.0'
        }
        try:
            response = self.s.put(url, headers=headers, data=payload, verify = False)
            print(response.text)
        except Exception as e:
            print(f"Caught exception {e}")
            return None

if __name__ == "__main__":
    # Might need to change back to port 443 (can now run on port 80)
    # OBS! Use port 80 for VC and port 443 for real robot!!!!!!!!!!
    mu = rws7('127.0.0.1')
    # u = rws7('10.47.89.50')
    r = mu.ip
    print(r)
##    mu.putfile()
##    mu.readfile()
    r = mu.getexecstat()   
    print(r)
    # print('----****----****----****----****----****----****----')
    # print(mu.getsymval())
    # print('----****----****----****----****----****----****----')
    print(mu.getsymval('T_ROB1','Module1','a'))
    # print('----****----****----****----****----****----****----')
    # print(mu.getsymval('T_ROB1','MainModule','nNbCycles'))
    # print('----****----****----****----****----****----****----')
    
##      nNbCycles   
    mu.stop()
    mu.reqmast()
    time.sleep(3)
    mu.setsymval('T_ROB1','Module1','b',15)
    time.sleep(3)
    #mu.pp2main()
    #time.sleep(3)
    mu.relmast()
    mu.start()
