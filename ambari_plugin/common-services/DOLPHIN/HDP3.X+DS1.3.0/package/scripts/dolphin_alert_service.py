"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import time
from resource_management import *

from dolphin_env import dolphin_env
import commands


class DolphinAlertService(Script):
    def install(self, env):
        import params
        env.set_params(params)
        Execute('rm -rf /usr/hdp/current/dolphinscheduler')
        Execute('wget {0} -O dolphinscheduler.tar.gz'.format(params.download_url))
        Execute('tar -zxvf dolphinscheduler.tar.gz -C {0} && rm -rf dolphinscheduler.tar.gz'.format(params.hdp_base_dir))
        Execute('rm -rf {1} && mv {0}/apache-dolphinscheduler* {1}'.format(params.hdp_base_dir,params.dolphin_home))
        Execute('wget -P {0}/lib/ {1}'.format(params.dolphin_home,params.jdbc_driver_download_url))
        Execute('ln -s {0} /usr/hdp/current/dolphinscheduler'.format(params.dolphin_home))


    def configure(self, env):
        import params
        params.pika_slave = True
        env.set_params(params)
        dolphin_env()

    def start(self, env):
        import params
        env.set_params(params)
        self.configure(env)
        no_op_test = format("ls {dolphin_pidfile_dir}/dolphinscheduler-alert-server.pid >/dev/null 2>&1 && ps `cat {dolphin_pidfile_dir}/dolphinscheduler-alert-server.pid` | grep `cat {dolphin_pidfile_dir}/dolphinscheduler-alert-server.pid` >/dev/null 2>&1")

        start_cmd = format("sh " + params.dolphin_bin_dir + "/dolphinscheduler-daemon.sh start alert-server")
        Execute(start_cmd, user=params.dolphin_user, not_if=no_op_test)

    def stop(self, env):
        import params
        env.set_params(params)
        stop_cmd = format("sh " + params.dolphin_bin_dir + "/dolphinscheduler-daemon.sh stop alert-server")
        Execute(stop_cmd, user=params.dolphin_user)
        time.sleep(5)

    def status(self, env):
        import status_params
        env.set_params(status_params)
        check_process_status(status_params.dolphin_run_dir + "dolphinscheduler-alert-server.pid")


if __name__ == "__main__":
    DolphinAlertService().execute()
