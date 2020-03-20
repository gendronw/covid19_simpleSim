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
beta, gamma = 0.12, 1./22

# total population
N = 8000000


#initial variable value for simulation
dates = np.array([datetime.date(2020, 3, 1)])

#S is suceptible population
#I is infected
#R is recover

dSdt = np.array([])
dIdt = np.array([])
dRdt = np.array([])

I = np.array([12])
R = np.array([0])
S = np.array([N-I[0]-R[0]])


R_value = np.array([beta/gamma])

date_index = 0

while (date_index < 240):
    #increment date
    dates = np.append(dates, [dates[date_index]+timedelta(days=1)])

    #calculate change in suceptible people
    dSdt = np.append(dSdt, -beta * S[date_index] * I[date_index] / N)

    #calculate change in infected people
    dIdt = np.append(dIdt, beta * S[date_index] * I[date_index] / N - gamma * I[date_index])

    #calculate cured people
    dRdt = np.append(dRdt, gamma * I[date_index])



    #calculate sum of cured and infected
    S = np.append(S, [S[date_index]+ dSdt[date_index]])
    R = np.append(R, [R[date_index] + dRdt[date_index]])
    I = np.append(I, [I[date_index] + dIdt[date_index]])

    R_value = np.append(R_value, beta/gamma)

    date_index = date_index + 1


#add empty value to derivative array so we can plot them
dIdt = np.append(dIdt, [0])

fig, (ax1, ax2, ax3) = plt.subplots(3)
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

ax3.bar(dates, dIdt, label='newly Infected')
ax3.legend()

plt.tight_layout()

plt.show()

print(dIdt)

#reference page for code
#https://scipython.com/book/chapter-8-scipy/additional-examples/the-sir-epidemic-model/

#reference for data
