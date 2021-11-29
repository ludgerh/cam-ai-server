# Copyright (C) 2021 Ludger Hellerhoff, ludger@booker-hellerhoff.de
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
# See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.


from concurrent import futures
from time import sleep
import psutil
from .c_tools import run_with_log
from .c_base import c_base
from .c_tfworker import tfworker

def displaystring(numberin):
  stringout = 'B'
  result = float(numberin)
  if result >= 100.0:
    result /= 1000.0
    stringout = 'K'
  if result >= 100.0:
    result /= 1000.0
    stringout = 'M'
  if result >= 100.0:
    result /= 1000.0
    stringout = 'G'
  if result >= 100.0:
    result /= 1000.0
    stringout = 'T'
  return(str(round(result, 3))+stringout)

def run(logger):
  i = 0
  while True:
    logstring = 'Health Status:'
    logger.info(logstring)
    logstring = ('Total Memory: ' + displaystring(psutil.virtual_memory().total))
    logstring += (' Used Memory: ' + displaystring(psutil.virtual_memory().used))
    logstring += (' ' + str(psutil.virtual_memory().percent) + '% --')
    logstring += (' Total Swap: ' + displaystring(psutil.swap_memory().total))
    logstring += (' Used Swap: ' + displaystring(psutil.swap_memory().used))
    logstring += (' ' + str(psutil.swap_memory().percent) + '%')
    logger.info(logstring)
    logstring = str(psutil.cpu_count())
    logstring += (' CPUs Usage: ' + str(psutil.cpu_percent()) + '% --')
    logstring += (' CPU Freq: ' + str(round(psutil.cpu_freq().current, 1)))
    logstring += (' Freq Max: ' + str(psutil.cpu_freq().max))
    logger.info(logstring)
    inqueuetotal = 0
    outqueuetotal = 0
    for user in tfworker.users:
      inqueuetotal += tfworker.users[user].fifoin.qsize()
      outqueuetotal += tfworker.users[user].fifoout.qsize()
    logstring = str(len(tfworker.users)) + ' TFW-Users: '
    logstring += (' InQueue Total: ' + str(inqueuetotal))
    logstring += (' OutQueue Total: ' + str(outqueuetotal))
    logger.info(logstring)
    viewqueuetotal = 0
    for view in c_base.instances['E']:
      viewqueuetotal += len(c_base.instances['E'][view].frameslist)
    logstring = str(len(c_base.instances['E'])) + ' Cached Views: '
    logstring += (' ViewQueue Total: ' + str(viewqueuetotal))
    logger.info(logstring)

    sleep(5)

executor = futures.ThreadPoolExecutor(max_workers=1)
run_with_log(executor, run, 'health')
