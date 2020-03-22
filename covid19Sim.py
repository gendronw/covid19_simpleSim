import matplotlib.pyplot as plt
from matplotlib.dates import (DAILY, DateFormatter,
                              rrulewrapper, RRuleLocator, drange)
import numpy as np
import datetime
from datetime import timedelta

rule = rrulewrapper(DAILY, interval=5)
loc = RRuleLocator(rule)
formatter = DateFormatter('%m/%d/%y')

# -------set simulation parameter--------------
# Contact rate, beta, and mean recovery rate, gamma, (in 1/days).
beta  = 0.10
daysInfectionIsActive = 26
gamma = 1/daysInfectionIsActive

# total population
N = 8000000


#initial variable value for simulation
dates = np.array([datetime.date(2020, 3, 1)])

#S is suceptible population
#I is infected
#R is recovered
#D is dead

dSdt = np.array([0])
dIdt = np.array([0])
dRdt = np.array([0])
dDdt = np.array([0])

I = np.array([12])
R = np.array([0])
S = np.array([N-I[0]-R[0]])
D = np.array([0])

infected_daily = np.array([0])

R_value = np.array([beta/gamma])

date_index = 0


#-------------health system variable-------------
hlt_days_to_get_to_hospital = 10
hlt_ratio_people_need_hospital = 0.10
hlt_ratio_people_need_ICU = 0.01
hlt_ratio_people_die = 0.006

hlt_normalBed = np.array([10000])
hlt_ICU_bed = np.array([1000])

dayIndex_toCountDead = 20


while (date_index < 365):
    #increment date
    dates = np.append(dates, [dates[date_index]+timedelta(days=1)])

    #calculate change in suceptible people
    dSdt = np.append(dSdt, -beta * S[date_index] * I[date_index] / N)

    #calculate change in infected people
    dIdt = np.append(dIdt, beta * S[date_index] * I[date_index] / N - gamma * I[date_index])

    #calculate cured people
    dRdt = np.append(dRdt, gamma * I[date_index])




    #calculate sum of cured and infected
    S = np.append(S, [S[date_index] + dSdt[date_index]])
    R = np.append(R, [R[date_index] + dRdt[date_index]])
    I = np.append(I, [I[date_index] + dIdt[date_index]])

    R_value = np.append(R_value, beta/gamma)

    date_index = date_index + 1

    #calculate daily infected
    if date_index > daysInfectionIsActive:
        infected_daily = np.append(infected_daily, [(dIdt[date_index] + dRdt[date_index])])
        if infected_daily[date_index] < 0:
            infected_daily[date_index] = 0
    else:
        infected_daily = np.append(infected_daily, [dIdt[date_index]])

    #calculate Dead
    if date_index > dayIndex_toCountDead:
        dDdt = np.append(dDdt, [infected_daily[date_index-dayIndex_toCountDead]*hlt_ratio_people_die])
        D = np.append(D, [D[date_index-1]+dDdt[date_index]])
    else:
        D = np.append(D, [0+D[date_index-1]])
        dDdt = np.append(dDdt, [0])

    #remove dead from infected
    I[date_index] = I[date_index] - dDdt[date_index]




#create Covid-19 figure
fig, (ax1, ax2, ax3, ax4) = plt.subplots(4)
fig.suptitle('Covid-19 Quebec simulation')
ax1.plot_date(dates, I, label='infected')
ax1.plot_date(dates, R, label='recovered')
ax1.legend()
#graph_infectedPersons.xaxis.set_major_locator(loc)
#ax1.xaxis.set_major_formatter(formatter)
ax1.xaxis.set_tick_params(rotation=90, labelsize=10)

ax2.plot_date(dates, R_value, label='rvalue')
ax2.xaxis.set_tick_params(rotation=90, labelsize=10)
ax2.legend()

ax3.bar(dates, dIdt, label='Infected variation')
ax3.legend()

ax4.plot_date(dates, infected_daily, label='Newly infected')
ax4.legend()

plt.tight_layout()

plt.show()


#create health care figure
fig, (ax1, ax2, ax3, ax4) = plt.subplots(4)
fig.suptitle('Health care Covid-19 Quebec simulation')
ax1.plot_date(dates, I, label='infected')
ax1.plot_date(dates, R, label='recovered')
ax1.legend()
#graph_infectedPersons.xaxis.set_major_locator(loc)
#ax1.xaxis.set_major_formatter(formatter)
ax1.xaxis.set_tick_params(rotation=90, labelsize=10)

ax2.plot_date(dates, R_value, label='rvalue')
ax2.xaxis.set_tick_params(rotation=90, labelsize=10)
ax2.legend()

ax3.bar(dates, dIdt, label='Infected variation')
ax3.legend()

ax4.plot_date(dates, D, label='dead')
ax4.legend()

plt.tight_layout()

plt.show()

print(dIdt)

#reference page for code
#https://scipython.com/book/chapter-8-scipy/additional-examples/the-sir-epidemic-model/

#reference for data
