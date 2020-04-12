import matplotlib.pyplot as plt
from matplotlib.dates import (DAILY, DateFormatter,
                              rrulewrapper, RRuleLocator, drange)
import numpy as np
import datetime
from datetime import timedelta

formatter = DateFormatter('%m/%d/%y')

# -------set simulation parameter--------------
# Contact rate, beta, and mean recovery rate, gamma, (in 1/days).
beta_original = 0.10
beta_to_reach = 0.10
beta = 0.10

daysInfectionIsActive = 26
gamma = 1/daysInfectionIsActive

# total population
N = 8000000

# initial variable value for simulation
dates = np.array([datetime.date(2020, 2, 10)])

# S is suceptible population
# I is infected
# R is recovered
# D is dead

dSdt = np.array([0])
dIdt = np.array([0])
dRdt = np.array([0])
dDdt = np.array([0])

I = np.array([1000])
R = np.array([0])
S = np.array([N-I[0]-R[0]])
D = np.array([0])

infected_daily = np.array([0])

R_value = np.array([beta/gamma])

date_index = 0


# -------------health system variable-------------
hlt_days_to_get_to_hospital = 10
hlt_days_normalbed_stay = 10
hlt_ratio_people_need_hospital = 0.10
hlt_ratio_people_need_ICU = 0.01
hlt_ratio_people_die = 0.02

hlt_normalBed_available = 8000
hlt_ICU_bed_available = 600

hlt_newNormalBed_need = np.array([0])
hlt_ICU_Bed_need = np.array([0])

hlt_normalBed_inUsed = np.array([0])
hlt_ICU_bed_inUsed = np.array([0])

hlt_normalBed_overflow = np.array([0])
hlt_ICU_bed_overflow = np.array([0])

dayIndex_toCountDead = 20

# -------------dynamic R0 : social distancing rating -------------

construction_workers = 0.05
work_From_Home = 0.15
School_And_KinderGarden = 0.20
cegep_And_University = 0.10
two_Meter_Rule = 0.25
sunday_Close_Shop = 0.03
essential_Shop = 0.22

begin_Social_Distancing = datetime.date(2020, 3, 14)

start_Construction = datetime.date(2020, 4, 27)
start_school_before_summer = datetime.date(2020, 5, 19)
close_school_summer = datetime.date(2020, 6, 20)
start_school_september = datetime.date(2020, 8, 24)


#socail activity of 1 mean a population without social distancing
socialActivity = np.array([1])

while (date_index < 300):
    # increment date
    dates = np.append(dates, [dates[date_index]+timedelta(days=1)])

    #look to start social distancing
    if(dates[date_index+1] == begin_Social_Distancing):
        socialActivity = np.append(socialActivity, socialActivity[date_index]-
                                   (construction_workers + work_From_Home + School_And_KinderGarden
                                    + cegep_And_University + two_Meter_Rule + sunday_Close_Shop))
        beta_to_reach = socialActivity[date_index+1] * beta_original
    elif(dates[date_index+1] == close_school_summer):
        socialActivity = np.append(socialActivity, socialActivity[date_index]-School_And_KinderGarden)
        beta_to_reach = socialActivity[date_index+1] * beta_original

    #look to remove social distancing
    elif(dates[date_index+1] == start_Construction):
        socialActivity = np.append(socialActivity, socialActivity[date_index] + construction_workers)
        beta_to_reach = socialActivity[date_index + 1] * beta_original
    elif (dates[date_index + 1] == start_school_before_summer):
        socialActivity = np.append(socialActivity, socialActivity[date_index] + School_And_KinderGarden)
        beta_to_reach = socialActivity[date_index + 1] * beta_original
    elif (dates[date_index + 1] == start_school_september):
        socialActivity = np.append(socialActivity, socialActivity[date_index] + School_And_KinderGarden + cegep_And_University)
        beta_to_reach = socialActivity[date_index + 1] * beta_original

    else:
        socialActivity = np.append(socialActivity, socialActivity[date_index])


    #move slowly beta to wanted number
    if beta < beta_to_reach:
        beta = beta + 0.002
    elif beta > beta_to_reach:
        beta = beta - 0.002

    # calculate change in suceptible people
    dSdt = np.append(dSdt, -beta * S[date_index] * I[date_index] / N)

    # calculate change in infected people
    dIdt = np.append(dIdt, beta * S[date_index] * I[date_index] / N - gamma * I[date_index])

    # calculate cured people
    dRdt = np.append(dRdt, gamma * I[date_index])

    # calculate sum of cured and infected
    S = np.append(S, [S[date_index] + dSdt[date_index]])
    R = np.append(R, [R[date_index] + dRdt[date_index]])
    I = np.append(I, [I[date_index] + dIdt[date_index]])

    R_value = np.append(R_value, beta/gamma)

    date_index = date_index + 1

    # calculate daily infected
    #if date_index > daysInfectionIsActive:
    infected_daily = np.append(infected_daily, [(dIdt[date_index] + dRdt[date_index])])
    #    if infected_daily[date_index] < 0:
    #        infected_daily[date_index] = 0
    #else:
    #    infected_daily = np.append(infected_daily, [dIdt[date_index]])

    # ------calculate used normal hospital bed-------
    if date_index > hlt_days_to_get_to_hospital:
        hlt_newNormalBed_need = np.append(hlt_newNormalBed_need, [infected_daily[date_index-hlt_days_to_get_to_hospital]*hlt_ratio_people_need_hospital])
        # copy last day bed used to this day
        hlt_normalBed_inUsed = np.append(hlt_normalBed_inUsed, [hlt_normalBed_inUsed[date_index - 1]])
        #removed saved person
        if date_index > (hlt_days_normalbed_stay + hlt_days_to_get_to_hospital):
            hlt_normalBed_inUsed[date_index] = hlt_normalBed_inUsed[date_index]-hlt_newNormalBed_need[date_index-hlt_days_normalbed_stay]
    else:
        hlt_normalBed_inUsed = np.append(hlt_normalBed_inUsed, [0])
        hlt_newNormalBed_need = np.append(hlt_newNormalBed_need, [0])

    # floor it to 0
    if hlt_normalBed_inUsed[date_index] < 0:
        hlt_normalBed_inUsed[date_index] = 0
    # add new beds used
    hlt_normalBed_inUsed[date_index] = hlt_normalBed_inUsed[date_index] + hlt_newNormalBed_need[date_index]

    # check for normal bed overflow
    if hlt_normalBed_inUsed[date_index] > hlt_normalBed_available:
        hlt_normalBed_overflow = np.append(hlt_normalBed_overflow, [hlt_normalBed_inUsed[date_index] - hlt_normalBed_available])
        hlt_normalBed_inUsed[date_index] = hlt_normalBed_available
    else:
        hlt_normalBed_overflow = np.append(hlt_normalBed_overflow, [0])
    # -----------------------------------------------

    # -------calculate used ICU hospital bed-------

    # ---------------------------------------------

    #calculate Dead
    if date_index > dayIndex_toCountDead:
        dDdt = np.append(dDdt, [infected_daily[date_index-dayIndex_toCountDead]*hlt_ratio_people_die])
        D = np.append(D, [D[date_index-1]+dDdt[date_index]])
    else:
        D = np.append(D, [0+D[date_index-1]])
        dDdt = np.append(dDdt, [0])
    #bed overflow goes directly to dead
    dDdt[date_index] = dDdt[date_index]+hlt_normalBed_overflow[date_index]

    #remove dead from infected
    I[date_index] = I[date_index] - dDdt[date_index]

# create Covid-19 figure
fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, sharex=True)
fig.suptitle('Covid-19 Quebec simulation')
ax1.plot_date(dates, I, label='infected')
ax1.plot_date(dates, R, label='recovered')
ax1.xaxis.set_tick_params(rotation=90, labelsize=10)
ax1.legend()

ax2.plot_date(dates, R_value, label='R0_value & social activity')
ax2.xaxis.set_tick_params(rotation=90, labelsize=10)
ax2.legend()

ax2_twin = ax2.twinx()
ax2_twin.set_ylabel('social', color='r')  # we already handled the x-label with ax1
ax2_twin.plot_date(dates, socialActivity, color = 'r')


ax3.bar(dates, dIdt, label='Infected variation')
ax3.plot_date(dates, infected_daily, color='k', label='Newly infected')
ax3.legend()

ax4.plot_date(dates, D, label='dead')
ax4.bar(dates, dDdt, color='r', label='dead variation')
ax4.legend()

plt.tight_layout()
plt.show()


# create health care figure
fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, sharex=True)
fig.suptitle('Health care Covid-19 Quebec simulation')
ax1.plot_date(dates, hlt_normalBed_inUsed, label='normal hospital Bed in use')
ax1.plot_date(dates, hlt_normalBed_overflow, label='normal bed overflow')
ax1.xaxis.set_tick_params(rotation=90, labelsize=10)
ax1.legend()

ax2.plot_date(dates, hlt_newNormalBed_need, label='new normal bed need')
ax2.xaxis.set_tick_params(rotation=90, labelsize=10)
ax2.legend()

ax3.bar(dates, dIdt, label='Infected variation')
ax3.plot_date(dates, infected_daily, color='k', label='Newly infected')
ax3.legend()

ax4.plot_date(dates, D, label='dead')
ax4.bar(dates, dDdt, color='r', label='dead variation')
ax4.legend()

plt.tight_layout()

plt.show()

print(dIdt)

#reference page for code
#https://scipython.com/book/chapter-8-scipy/additional-examples/the-sir-epidemic-model/

#reference for data
