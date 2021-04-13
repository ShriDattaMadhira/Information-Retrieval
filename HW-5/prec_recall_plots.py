import matplotlib.pyplot as plt

# Import Data
prec_q1, prec_q2, prec_q3 = [], [], []
rec_q1, rec_q2, rec_q3 = [], [], []
f = open("trec_eval_results.txt", "r")
for line in f:
    line = line.split()
    if line[0] == "152101":
        prec_q1.append(float(line[4]))
        rec_q1.append(float(line[5]))
    elif line[0] == "152102":
        prec_q2.append(float(line[4]))
        rec_q2.append(float(line[5]))
    elif line[0] == "152103":
        prec_q3.append(float(line[4]))
        rec_q3.append(float(line[5]))
f.close()

fig, axs = plt.subplots(3, 1)
axs[0].plot(rec_q1, prec_q1)
axs[0].set_xlim(0, 1)
axs[0].set_xlabel('Recall')
axs[0].set_ylabel('Precision')
axs[0].grid(True)

axs[1].plot(rec_q2, prec_q2)
axs[1].set_xlim(0, 1)
axs[1].set_xlabel('Recall')
axs[1].set_ylabel('Precision')
axs[1].grid(True)

axs[2].plot(rec_q3, prec_q3)
axs[2].set_xlim(0, 1)
axs[2].set_xlabel('Recall')
axs[2].set_ylabel('Precision')
axs[2].grid(True)

plt.show()
