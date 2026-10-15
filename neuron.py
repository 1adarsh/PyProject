import matplotlib.pyplot as plt


# Leak integrate and fire model of a Neuron
## workflow of model
## Input -> Integrate -> leak -> membrane V -> if V >= threshold -> spike -> reset  
## here LIF equation
## t_m * dv/dt = -(V-V_rest) + RI
## Where 
### V = membrane potential
### V_rest = membrane potential at rest.
### I = Input current.
### t_m = membrane time constant


V_rest = -70 
V = -70
R = 1
tau = 10

dt = 1
threshold = -55
reset = -70

voltage = []
current = []
spike_time = []
no_of_spikes = 0
times = []

for step in range(500):
    if step < 30:
        I = 0
    elif step < 70:
        I = 20
    else:
        I = 0
    print(step, I)
    dv_dt = (-(V-V_rest) + R*I)/ tau
    print(f"potencial difference at this {step} is {dv_dt}")
    V  = V + dv_dt * dt
    print(f"voltage at this {step} is {V}")
    if V >= threshold:
        spike_time.append(step)
        no_of_spikes += 1
        V = reset
    voltage.append(V)
    current.append(I)
    times.append(step)

print("max voltage", max(voltage))
print("current", current)
print("Spike time:", spike_time)
print("No of spike", no_of_spikes) 


plt.figure(figsize=(12, 12))
plt.plot(times, voltage, label='Membrane Potential (V)')
plt.axhline(y=threshold, color='r', linestyle='--', label='Threshold')
for spike in spike_time:
    plt.axvline(x=spike, color='g', linestyle='--', label='Spike' if spike == spike_time[0] else "")
plt.xlabel('Time')
plt.ylabel('Voltage')
plt.title('LIF Neuron Model')
plt.legend()
plt.show()
