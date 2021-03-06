# -*- mode: python; coding: utf-8 -*-
# Copyright 2016 the HERA Collaboration
# Licensed under the 2-clause BSD license.

"""Testing for `hera_mc.rtp`.

"""
from __future__ import absolute_import, division, print_function

import unittest
from math import floor
import numpy as np
from astropy.time import Time, TimeDelta
from sqlalchemy.exc import NoForeignKeysError

from .. import mc, cm_transfer
from ..rtp import RTPStatus, RTPProcessEvent, RTPProcessRecord, RTPTaskResourceRecord
from .. import utils, geo_location
from ..tests import TestHERAMC


class TestRTP(TestHERAMC):

    def setUp(self):
        super(TestRTP, self).setUp()

        time = Time.now()
        obsid = utils.calculate_obsid(time)
        self.observation_names = ['starttime', 'stoptime', 'obsid']
        self.observation_values = [time, time + TimeDelta(10 * 60, format='sec'),
                                   obsid]
        self.observation_columns = dict(zip(self.observation_names,
                                            self.observation_values))
        self.status_names = ['time', 'status', 'event_min_elapsed',
                             'num_processes', 'restart_hours_elapsed']
        self.status_values = [time, 'happy', 3.6, 8, 10.2]
        self.status_columns = dict(zip(self.status_names, self.status_values))

        self.event_names = ['time', 'obsid', 'event']
        self.event_values = [time, obsid, 'queued']
        self.event_columns = dict(zip(self.event_names, self.event_values))

        self.record_names = ['time', 'obsid', 'pipeline_list', 'rtp_git_version', 'rtp_git_hash',
                             'hera_qm_git_version', 'hera_qm_git_hash', 'hera_cal_git_version',
                             'hera_cal_git_hash', 'pyuvdata_git_version', 'pyuvdata_git_hash']
        self.record_values = [time, obsid, 'sample_pipe', 'v0.0.1', 'lskdjf24l', 'v0.1.0', 'abcd34d',
                              'v1.0.0', 'jkfldi39', 'v2.0.0', 'fjklj828']
        self.record_columns = dict(zip(self.record_names, self.record_values))

        self.task_resource_names = ['obsid', 'task_name', 'start_time', 'stop_time', 'max_memory',
                                    'avg_cpu_load']
        self.task_resource_values = [obsid, 'OMNICAL', time, time + TimeDelta(10 * 60, format='sec'),
                                     16.2, 1.01]
        self.task_resource_columns = dict(zip(self.task_resource_names, self.task_resource_values))

    def test_add_rtp_status(self):
        self.test_session.add_rtp_status(*self.status_values)

        exp_columns = self.status_columns.copy()
        exp_columns['time'] = int(floor(exp_columns['time'].gps))
        expected = RTPStatus(**exp_columns)

        result = self.test_session.get_rtp_status(self.status_columns['time']
                                                  - TimeDelta(2, format='sec'))
        self.assertEqual(len(result), 1)
        result = result[0]

        self.assertTrue(result.isclose(expected))

        new_status_time = self.status_columns['time'] + TimeDelta(5 * 60, format='sec')
        new_status = 'unhappy'
        self.test_session.add_rtp_status(new_status_time,
                                         new_status,
                                         self.status_columns['event_min_elapsed'] + 5,
                                         self.status_columns['num_processes'],
                                         self.status_columns['restart_hours_elapsed'] + 5. / 60.)

        result_mult = self.test_session.get_rtp_status(self.status_columns['time']
                                                       - TimeDelta(2, format='sec'),
                                                       stoptime=new_status_time)
        self.assertEqual(len(result_mult), 2)

        result2 = self.test_session.get_rtp_status(new_status_time
                                                   - TimeDelta(2, format='sec'))
        self.assertEqual(len(result2), 1)
        result2 = result2[0]
        self.assertFalse(result2.isclose(expected))

    def test_errors_rtp_status(self):
        self.assertRaises(ValueError, self.test_session.add_rtp_status, 'foo',
                          *self.status_values[1:])

        self.test_session.add_rtp_status(*self.status_values)
        self.assertRaises(ValueError, self.test_session.get_rtp_status, 'unhappy')
        self.assertRaises(ValueError, self.test_session.get_rtp_status,
                          self.status_columns['time'], stoptime='unhappy')

    def test_add_rtp_process_event(self):
        # raise error if try to add process event with unmatched obsid
        # self.assertRaises(NoForeignKeysError, self.test_session.add_rtp_process_event,
        #                   self.event_values[0], self.event_values[1] + 2,
        #                   self.event_values[2])

        self.test_session.add_obs(*self.observation_values)
        obs_result = self.test_session.get_obs()
        self.assertTrue(len(obs_result), 1)

        self.test_session.add_rtp_process_event(*self.event_values)

        exp_columns = self.event_columns.copy()
        exp_columns['time'] = int(floor(exp_columns['time'].gps))
        expected = RTPProcessEvent(**exp_columns)

        result = self.test_session.get_rtp_process_event(self.event_columns['time']
                                                         - TimeDelta(2, format='sec'))
        self.assertEqual(len(result), 1)
        result = result[0]
        result_obsid = self.test_session.get_rtp_process_event(self.event_columns['time']
                                                               - TimeDelta(2, format='sec'),
                                                               obsid=self.event_columns['obsid'])
        self.assertEqual(len(result_obsid), 1)
        result_obsid = result_obsid[0]
        self.assertTrue(result.isclose(expected))

        new_obsid_time = self.event_columns['time'] + TimeDelta(3 * 60, format='sec')
        new_obsid = utils.calculate_obsid(new_obsid_time)
        self.test_session.add_obs(Time(new_obsid_time),
                                  Time(new_obsid_time + TimeDelta(10 * 60, format='sec')),
                                  new_obsid)
        obs_result = self.test_session.get_obs(obsid=new_obsid)
        self.assertEqual(obs_result[0].obsid, new_obsid)

        self.test_session.add_rtp_process_event(new_obsid_time,
                                                new_obsid,
                                                self.event_columns['event'])
        result_obsid = self.test_session.get_rtp_process_event(self.event_columns['time']
                                                               - TimeDelta(2, format='sec'),
                                                               obsid=self.event_columns['obsid'])
        self.assertEqual(len(result_obsid), 1)
        result_obsid = result_obsid[0]
        self.assertTrue(result_obsid.isclose(expected))

        new_event_time = self.event_columns['time'] + TimeDelta(5 * 60, format='sec')
        new_event = 'started'
        self.test_session.add_rtp_process_event(new_event_time,
                                                self.event_columns['obsid'],
                                                new_event)

        result_mult = self.test_session.get_rtp_process_event(self.event_columns['time']
                                                              - TimeDelta(2, format='sec'),
                                                              stoptime=new_event_time)
        self.assertEqual(len(result_mult), 3)

        result_mult_obsid = self.test_session.get_rtp_process_event(self.event_columns['time']
                                                                    - TimeDelta(2, format='sec'),
                                                                    stoptime=new_event_time,
                                                                    obsid=self.event_columns['obsid'])
        self.assertEqual(len(result_mult_obsid), 2)

        result_new_obsid = self.test_session.get_rtp_process_event(self.event_columns['time']
                                                                   - TimeDelta(2, format='sec'),
                                                                   obsid=new_obsid)
        self.assertEqual(len(result_new_obsid), 1)
        result_new_obsid = result_new_obsid[0]
        self.assertFalse(result_new_obsid.isclose(expected))

    def test_errors_rtp_process_event(self):
        self.test_session.add_obs(*self.observation_values)
        obs_result = self.test_session.get_obs()
        self.assertTrue(len(obs_result), 1)

        self.assertRaises(ValueError, self.test_session.add_rtp_process_event, 'foo',
                          *self.event_values[1:])

        self.test_session.add_rtp_process_event(*self.event_values)
        self.assertRaises(ValueError, self.test_session.get_rtp_process_event, 'foo')
        self.assertRaises(ValueError, self.test_session.get_rtp_process_event,
                          self.event_columns['time'], stoptime='bar')

        # raise error if pass value not in enum
        # self.assertRaises(ValueError, self.test_session.add_rtp_process_event,
        #                   self.event_columns['time'], self.event_columns['obsid'],
        #                   'foo')

    def test_classes_not_equal(self):
        self.test_session.add_obs(*self.observation_values)
        obs_result = self.test_session.get_obs()
        self.assertTrue(len(obs_result), 1)

        self.test_session.add_rtp_process_event(*self.event_values)
        self.test_session.add_rtp_status(*self.status_values)

        status_result = self.test_session.get_rtp_status(self.status_columns['time']
                                                         - TimeDelta(2, format='sec'))
        self.assertEqual(len(status_result), 1)
        status_result = status_result[0]
        event_result = self.test_session.get_rtp_process_event(self.event_columns['time']
                                                               - TimeDelta(2, format='sec'))
        self.assertFalse(status_result.isclose(event_result))

    def test_add_rtp_process_record(self):
        # raise error if try to add process event with unmatched obsid
        # self.assertRaises(NoForeignKeysError, self.test_session.add_rtp_process_record,
        #                   self.record_values[0], self.record_values[1] + 2,
        #                   self.record_values[2:5])

        self.test_session.add_obs(*self.observation_values)
        obs_result = self.test_session.get_obs()
        self.assertTrue(len(obs_result), 1)

        self.test_session.add_rtp_process_record(*self.record_values)

        exp_columns = self.record_columns.copy()
        exp_columns['time'] = int(floor(exp_columns['time'].gps))
        expected = RTPProcessRecord(**exp_columns)

        result = self.test_session.get_rtp_process_record(self.record_columns['time']
                                                          - TimeDelta(2, format='sec'))
        self.assertEqual(len(result), 1)
        result = result[0]
        self.assertTrue(result.isclose(expected))

        result_obsid = self.test_session.get_rtp_process_record(self.record_columns['time']
                                                                - TimeDelta(2, format='sec'),
                                                                obsid=self.record_columns['obsid'])
        self.assertEqual(len(result_obsid), 1)
        result_obsid = result_obsid[0]
        self.assertTrue(result_obsid.isclose(expected))

        new_obsid_time = self.record_columns['time'] + TimeDelta(3 * 60, format='sec')
        new_obsid = utils.calculate_obsid(new_obsid_time)
        self.test_session.add_obs(Time(new_obsid_time),
                                  Time(new_obsid_time + TimeDelta(10 * 60, format='sec')),
                                  new_obsid)
        obs_result = self.test_session.get_obs(obsid=new_obsid)
        self.assertEqual(obs_result[0].obsid, new_obsid)

        self.test_session.add_rtp_process_record(new_obsid_time,
                                                 new_obsid,
                                                 *self.record_values[2:11])
        result_obsid = self.test_session.get_rtp_process_record(self.record_columns['time']
                                                                - TimeDelta(2, format='sec'),
                                                                obsid=self.record_columns['obsid'])
        self.assertEqual(len(result_obsid), 1)
        result_obsid = result_obsid[0]
        self.assertTrue(result_obsid.isclose(expected))

        new_record_time = self.record_columns['time'] + TimeDelta(5 * 60, format='sec')
        new_pipeline = 'new_pipe'
        self.test_session.add_rtp_process_record(new_record_time,
                                                 self.record_columns['obsid'],
                                                 new_pipeline, *self.record_values[3:11])

        result_mult = self.test_session.get_rtp_process_record(self.record_columns['time']
                                                               - TimeDelta(2, format='sec'),
                                                               stoptime=new_record_time)
        self.assertEqual(len(result_mult), 3)

        result_mult_obsid = self.test_session.get_rtp_process_record(self.record_columns['time']
                                                                     - TimeDelta(2, format='sec'),
                                                                     stoptime=new_record_time,
                                                                     obsid=self.record_columns['obsid'])
        self.assertEqual(len(result_mult_obsid), 2)

        result_new_obsid = self.test_session.get_rtp_process_record(self.record_columns['time']
                                                                    - TimeDelta(2, format='sec'),
                                                                    obsid=new_obsid)
        self.assertEqual(len(result_new_obsid), 1)
        result_new_obsid = result_new_obsid[0]

        self.assertFalse(result_new_obsid.isclose(expected))

    def test_errors_rtp_process_record(self):
        self.test_session.add_obs(*self.observation_values)
        obs_result = self.test_session.get_obs()
        self.assertTrue(len(obs_result), 1)

        fake_vals = [1., 'a', 2., 'b', 3., 'c', 4., 'd', 5., 'e']
        self.assertRaises(ValueError, self.test_session.add_rtp_process_record, 'foo',
                          *fake_vals)

        self.test_session.add_rtp_process_record(*self.record_values)
        self.assertRaises(ValueError, self.test_session.get_rtp_process_record, 'foo')
        self.assertRaises(ValueError, self.test_session.get_rtp_process_record,
                          self.record_columns['time'], stoptime='bar')

    def test_add_rtp_task_resource_record(self):
        self.test_session.add_obs(*self.observation_values)
        obs_result = self.test_session.get_obs()
        self.assertTrue(len(obs_result), 1)

        self.test_session.add_rtp_task_resource_record(*self.task_resource_values)

        exp_columns = self.task_resource_columns.copy()
        exp_columns['start_time'] = int(floor(exp_columns['start_time'].gps))
        exp_columns['stop_time'] = int(floor(exp_columns['stop_time'].gps))
        expected = RTPTaskResourceRecord(**exp_columns)

        result = self.test_session.get_rtp_task_resource_record(
            starttime=self.task_resource_columns['start_time'] - TimeDelta(2, format='sec'),
            obsid=self.task_resource_columns['obsid'])
        self.assertEqual(len(result), 1)
        result = result[0]
        self.assertTrue(result.isclose(expected))

        new_task_time = self.task_resource_columns['start_time'] + TimeDelta(60, format='sec')
        new_task = 'task2'
        self.test_session.add_rtp_task_resource_record(
            self.task_resource_columns['obsid'], new_task, new_task_time,
            *self.task_resource_values[3:])

        result = self.test_session.get_rtp_task_resource_record(
            starttime=self.task_resource_columns['start_time'] - TimeDelta(2, format='sec'),
            obsid=self.task_resource_columns['obsid'])
        self.assertEqual(len(result), 1)
        result = result[0]
        self.assertTrue(result.isclose(expected))

        result = self.test_session.get_rtp_task_resource_record(
            starttime=self.task_resource_columns['start_time'] - TimeDelta(2, format='sec'),
            obsid=self.task_resource_columns['obsid'],
            stoptime=self.task_resource_columns['start_time'] + TimeDelta(2 * 60, format='sec'))
        self.assertEqual(len(result), 2)

        result = self.test_session.get_rtp_task_resource_record(
            obsid=self.task_resource_columns['obsid'])
        self.assertEqual(len(result), 2)

        result = self.test_session.get_rtp_task_resource_record(
            starttime=self.task_resource_columns['start_time'] - TimeDelta(2, format='sec'),
            task_name=self.task_resource_columns['task_name'],
            stoptime=self.task_resource_columns['start_time'] + TimeDelta(2 * 60, format='sec'))
        self.assertEqual(len(result), 1)
        result = result[0]
        self.assertTrue(result.isclose(expected))

        new_task_time = self.task_resource_columns['start_time'] + TimeDelta(3 * 60, format='sec')

        new_obsid_time = self.task_resource_columns['start_time'] + TimeDelta(3 * 60, format='sec')
        new_obsid = utils.calculate_obsid(new_obsid_time)
        self.test_session.add_obs(Time(new_obsid_time),
                                  Time(new_obsid_time + TimeDelta(10 * 60, format='sec')),
                                  new_obsid)
        obs_result = self.test_session.get_obs(obsid=new_obsid)
        self.assertEqual(obs_result[0].obsid, new_obsid)

        self.test_session.add_rtp_task_resource_record(
            new_obsid, self.task_resource_columns['task_name'], new_task_time,
            *self.task_resource_values[3:])

        result = self.test_session.get_rtp_task_resource_record(
            starttime=self.task_resource_columns['start_time'] - TimeDelta(2, format='sec'),
            task_name=self.task_resource_columns['task_name'],
            stoptime=self.task_resource_columns['start_time'] + TimeDelta(5 * 60, format='sec'))
        self.assertEqual(len(result), 2)

        result = self.test_session.get_rtp_task_resource_record(
            starttime=self.task_resource_columns['start_time'] - TimeDelta(2, format='sec'),
            obsid=self.task_resource_columns['obsid'],
            task_name=self.task_resource_columns['task_name'],
            stoptime=self.task_resource_columns['start_time'] + TimeDelta(5 * 60, format='sec'))
        self.assertEqual(len(result), 1)
        result = result[0]
        self.assertTrue(result.isclose(expected))

        # test computed column
        elapsed = result.elapsed
        self.assertTrue(np.isclose(elapsed, 600.))

    def test_add_rtp_task_resource_record_nulls(self):
        self.test_session.add_obs(*self.observation_values)
        obs_result = self.test_session.get_obs()
        self.assertTrue(len(obs_result), 1)

        # don't pass in max_memory or avg_cpu_load
        self.test_session.add_rtp_task_resource_record(*self.task_resource_values[:-2])

        exp_columns = self.task_resource_columns.copy()
        # get rid of max_memory and avg_cpu_load columns
        exp_columns.pop('max_memory')
        exp_columns.pop('avg_cpu_load')
        exp_columns['start_time'] = int(floor(exp_columns['start_time'].gps))
        exp_columns['stop_time'] = int(floor(exp_columns['stop_time'].gps))
        expected = RTPTaskResourceRecord(**exp_columns)

        result = self.test_session.get_rtp_task_resource_record(
            starttime=self.task_resource_columns['start_time'] - TimeDelta(2, format='sec'),
            obsid=self.record_columns['obsid'])
        self.assertEqual(len(result), 1)
        result = result[0]
        self.assertTrue(result.isclose(expected))

    def test_errors_rtp_task_resource_record(self):
        self.test_session.add_obs(*self.observation_values)
        obs_result = self.test_session.get_obs()
        self.assertTrue(len(obs_result), 1)

        fake_vals = [1, 'a', 2, 'b', 3, 'c']
        self.assertRaises(ValueError, self.test_session.add_rtp_task_resource_record, *fake_vals)
        # test case where start_time is an astropy.time object, but stop_time isn't
        fake_vals2 = [1, 'a', Time.now(), 'b', 3, 'c']
        self.assertRaises(ValueError, self.test_session.add_rtp_task_resource_record, *fake_vals2)

        self.test_session.add_rtp_task_resource_record(*self.task_resource_values)
        self.assertRaises(ValueError, self.test_session.get_rtp_process_record, 1, 2)

        self.assertRaises(ValueError, self.test_session.get_rtp_task_resource_record,
                          task_name=self.task_resource_columns['task_name'])

        self.assertRaises(ValueError, self.test_session.get_rtp_task_resource_record)


if __name__ == '__main__':
    unittest.main()
