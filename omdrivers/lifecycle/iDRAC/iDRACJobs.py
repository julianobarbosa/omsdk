import os
import re
import time
import xml.etree.ElementTree as ET
from enum import Enum
from datetime import datetime
from omsdk.sdkprint import LogMan, pretty
from omsdk.sdkproto import PWSMAN,PREDFISH, PSNMP
from omsdk.sdkcenum import EnumWrapper, TypeHelper
from omsdk.lifecycle.sdkjobs import iBaseJobApi
import sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

try:
    from pysnmp.hlapi import *
    from pysnmp.smi import *
    PySnmpPresent = True
except ImportError:
    PySnmpPresent = False

JobStatusEnum = EnumWrapper("iDRACJSE",  {
    'Success' : 'Success',
    'InProgress' : 'InProgress',
    'Failed' : 'Failed',
    'Invalid' : 'Invalid',
    }).enum_type

ReturnValue = EnumWrapper("RV", {
    "Success" : 0,
    "Error" : 2,
    "JobCreated" : 4096,
    "Invalid" : -1,
    }).enum_type

iDRACJobsEnum = EnumWrapper("iDRACJobEnum", {
    "Jobs" : "Jobs",
    }).enum_type

class iDRACJobs(iBaseJobApi):
    def __init__(self, entity):
        if PY2:
            super(iDRACJobs, self).__init__(entity, iDRACJobsEnum)
        else:
            super().__init__(entity, iDRACJobsEnum)

    # joblist = [ 'JID_20123', 'JID_134' ]
    def queue_jobs(self, job_list, schtime):
        if not isinstance(job_list, list):
            job_list = [job_list]
        return self.entity._jobq_setup(jobs = job_list, startat=schtime)

    def delete_job(self, jobid):
        return self.entity._jobq_delete(jobid = jobid)

    def delete_all_jobs(self):
        return self.entity._jobq_delete(jobid ="JID_CLEARALL")

    def get_job_details(self, jobid):
        selector = { "InstanceID" : jobid }
        return self.entity.cfactory.opget(iDRACJobsEnum.Jobs, selector)

    def get_job_status(self, jobid):
        jobs = {}
        jobret = { "Status" : TypeHelper.resolve(JobStatusEnum.InProgress) }
        jobs = self.get_job_details(jobid)
        LogMan.debugjson(jobs)
        if "Status" in jobs and jobs['Status'] != "Success":
            print("ERROR: get_job_status failed: " + jobs['Status'])
            print("ERROR: get_job_status failed: " + jobs['Message'])
            return jobs

        jb = jobs['Data']['Jobs']
        if jb['InstanceID'] != jobid:
            print("ERROR: Job instance not found")
            return jobs
        if 'JobStatus' in jb:
            jobstatus = jb['JobStatus']
            if jobstatus == 'Completed':
                jobstaten = JobStatusEnum.Success
            elif 'Message' in jb and 'completed' in jb['Message']:
                jobstaten = JobStatusEnum.Success
            elif jobstatus == 'Failed':
                jobstaten = JobStatusEnum.Failed
            elif jobstatus == 'Pending':
                jobstaten = JobStatusEnum.InProgress
            elif jobstatus.endswith('In Progress'):
                jobstaten = JobStatusEnum.InProgress
            elif jobstatus.endswith('Scheduled'):
                jobstaten = JobStatusEnum.InProgress
            elif jobstatus.endswith('Running'):
                jobstaten = JobStatusEnum.InProgress
            elif jobstatus.endswith('Invalid'):
                jobstaten = JobStatusEnum.InProgress
            else:
                jobstaten = JobStatusEnum.InProgress
            jb['Status'] = TypeHelper.resolve(jobstaten)
        return jb


    def _parse_status_obj(self, retval):
        if not 'Status' in retval :
            retval['Status'] = "Invalid"
            retval['Message'] = "<empty result>"
            return (False, 'Invalid', None)
        elif retval['Status'] != 'Success':
            return (False, retval['Status'], None)
        LogMan.debugjson(retval)
        if retval['Return'] != "JobCreated":
            return (False, retval['Status'], None)
        if not 'Job' in retval or not 'JobId' in retval['Job']:
            LogMan.debugjson("Error: Jobid is not found, even though return says jobid")
            return (True, retval['Status'], None)
        jobid = retval['Job']['JobId']
        LogMan.debug("Job is " + jobid)
        if jobid is None:
            return (True, retval['Status'], None)
        return (True, retval['Status'], jobid)

    def _job_wait(self, fname, rjson, track_jobid = True, show_progress=False):
        (is_job_created, job_status, jobid) = self._parse_status_obj(rjson)
        rjson['file'] = fname
        if job_status != 'Success':
            rjson['retval'] = False
            return rjson
        elif not is_job_created:
            rjson['retval'] = True
            return rjson
        elif not jobid:
            rjson['retval'] = False
            return rjson
        rjson = self.job_wait(jobid, track_jobid, show_progress) 
        rjson['file'] = fname
        return rjson

    def job_wait(self, jobid, track_jobid = True, show_progress=False):
        if track_jobid:
            self.last_job = jobid
        ret_json = {}
        job_ret = False
        while True:
            status = self.get_job_status(jobid)
            if not 'Status' in status:
                print("Invalid Status")
            else:
                LogMan.debugjson(status)

                pcc = "0"
                msg = ""
                if 'PercentComplete' in status:
                    pcc = status['PercentComplete']
                if 'Message' in status:
                    msg = status['Message']
                if show_progress:
                    print("{0} : {1} : Percent Complete: {2} | Message = {3}".format(jobid, status['Status'], pcc, msg))
                if status['Status'] == TypeHelper.resolve(JobStatusEnum.Success):
                    if show_progress:
                        print("Message:" + status['Message'])
                    job_ret = True
                    ret_json = status
                    break
                elif status['Status'] != TypeHelper.resolve(JobStatusEnum.InProgress):
                    if show_progress:
                        print("Message:" + status['Message'])
                    job_ret = False
                    ret_json = status
                    break
                else:
                    LogMan.debug(str(status))
            time.sleep(2)
        ret_json['retval'] = job_ret
        return ret_json

    # End Job Functions
