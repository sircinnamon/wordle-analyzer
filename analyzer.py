import json
import statistics
from math import ceil, floor

B = 'black'
G = 'green'
Y = 'yellow'

# for breaking ties
LETTER_FREQ_MOD = {
	'a': 0.082,
	'b': 0.015,
	'c': 0.028,
	'd': 0.043,
	'e': 0.13,
	'f': 0.022,
	'g': 0.02,
	'h': 0.061,
	'i': 0.07,
	'j': 0.0015,
	'k': 0.077,
	'l': 0.04,
	'm': 0.025,
	'n': 0.067,
	'o': 0.075,
	'p': 0.019,
	'q': 0.00095,
	'r': 0.06,
	's': 0.063,
	't': 0.091,
	'u': 0.028,
	'v': 0.0098,
	'w': 0.024,
	'x': 0.0015,
	'y': 0.02,
	'z': 0.00074
}

def filter_wordlist(wordlist, guess):
	def filter_func(word):
		for i, l in enumerate(word):
			# Unmatched green
			if(guess[1][i]==G and l != guess[0][i]):
				return False
			# Matched Yellow
			if(guess[1][i]==Y and l == guess[0][i]):
				return False
			# Matched Black (in whole word)
			if(guess[1][i]==B and guess[0][i] in word):
				return False
			# Yellow not in whole word
			if(guess[1][i]==Y and guess[0][i] not in word):
				return False
		return True
	return list(filter(filter_func, wordlist))

def analyze_guess(wordlist, guessword):
	max_v = (0,[])
	amts = []
	for g1 in [B,Y,G]:
		for g2 in [B,Y,G]:
			for g3 in [B,Y,G]:
				for g4 in [B,Y,G]:
					for g5 in [B,Y,G]:
						valid = len(filter_wordlist(wordlist, (guessword, [g1,g2,g3,g4,g5])))
						if valid > max_v[0]:
							max_v = (valid, [g1,g2,g3,g4,g5])
						if valid > 0:
							amts.append(valid)
	return (max_v, statistics.mean(amts))

def make_guess(word, target):
	out = []
	for i, l in enumerate(word):
		if l == target[i]:
			out.append(G)
		elif l in target:
			out.append(Y)
		else:
			out.append(B)
	return out

def recommend_guess_by_analysis(wordlist, limit=1):
	progress_bar = True
	max_words = len(wordlist)
	min_w = (max_words, 0, '')
	analyzed = []
	for i, word in enumerate(wordlist):
		# if (progress_bar and (i % progress_bar_inc == 0)): print("|", end="\r", flush=True)
		a = analyze_guess(wordlist, word)
		analyzed.append((a[1], a[0][0], word)) # average, worstcase, word
		if progress_bar: print("\r[{:<50}]({}/{})".format("|"*(ceil(50*(i+1)/max_words)), i+1, max_words), end="", flush=True)
	analyzed.sort(key=lambda x: x[0])
	print("")
	return analyzed[:limit]

def reccomend_guess_by_unused(wordlist, limit=1):
	wl = wordlist.copy()
	letter_count = {}
	for l in ''.join(wordlist):
		if l in letter_count: letter_count[l]+=1
		else: letter_count[l]=1+LETTER_FREQ_MOD[l]
	# print(letter_count)
	letters_by_freq = list({k: v for k, v in sorted(letter_count.items(), key=lambda item: item[1])}.keys())
	out = []
	filtered_letters=0
	while(len(out) < limit):
		sub_wl = filter_by_common_letter(wl, freq=letters_by_freq)
		if(len(sub_wl)>limit and filtered_letters<5):
			wl = sub_wl
			filtered_letters+=1
		else:
			out += sub_wl
		
	wl = out[:limit]

	# words have been chosen, sort by analysis
	# print(limit, wl)
	def analyze_formatter(r):
		a = analyze_guess(wordlist, r)
		return (a[1], a[0][0], r) # average, worstcase, word

	rec_guesses = list(map(analyze_formatter, wl))
	rec_guesses.sort(key=lambda x: x[0])
	for rg in rec_guesses:
		print_analysis(rg[0], rg[1], rg[2], len(wordlist))
	return rec_guesses

def filter_by_common_letter(wordlist, freq):
	wl = wordlist.copy()
	def filter_func(x): return (freq[-1] in x)
	new_wl = list(filter(filter_func, wl))
	# print("Filter {} words by {} leaves {}".format(len(wl), freq[-1], len(new_wl)))
	del freq[-1]
	# print("{} {}".format(len(new_wl), len(wl)))
	return new_wl

def print_analysis(avg, worst, word, total):
	print("Guess analysis: {} - max {} ({:.0%}) - average {} ({:.0%})".format(
		word,
		worst,
		worst/total,
		avg,
		avg/total
	))

def print_recc(rec, total):
	print("Optimal guess: {} - max {} ({:.0%}) - average {} ({:.0%})".format(
		rec[2],
		rec[1],
		rec[1]/total,
		rec[0],
		rec[0]/total
	))

def dynamic_recommend(wordlist):
	if(len(wordlist)<100):
		reccs = recommend_guess_by_analysis(wordlist, limit=20)
		for r in reccs:
			print_recc(r, len(wordlist))
	else:
		reccs = reccomend_guess_by_unused(wordlist, limit=floor(60000/len(wordlist)))
	return reccs

def analyze_mode():
	print("input guesses (format \"guess BGYBB\") - Enter again to finish: ")
	guesses = []
	line = input()
	while(line != ""):
		guesses.append(parse_guess(line))
		line = input()
	
	with open("./wordlist.json") as wordfile:
		words = json.load(wordfile)
		

		print("Possible words: {}".format(len(words)))
		wordlist = words.copy()
		print("STAGE {} - {} WORDS REMAIN".format(0, len(wordlist)))
		reccomend_guess_by_unused(words, limit=3)
		for i, g in enumerate(guesses):
			wordlist = filter_wordlist(wordlist, g)
			print("STAGE {} - {} WORDS REMAIN".format(i+1, len(wordlist)))
			dynamic_recommend(wordlist)

def ai_mode():
	print("input target word: ", end="", flush=True)
	target = input().lower()[:5]
	with open("./wordlist.json") as wordfile:
		words = json.load(wordfile)
		wordlist = words.copy()
		if(target not in words):
			print("Word not in dict!")
			return
		rnd = 0
		curr_word = ""
		while curr_word != target:
			print("STAGE {} - {} WORDS REMAIN".format(rnd, len(wordlist)))
			reccs =  dynamic_recommend(wordlist)
			curr_word = reccs[0][2]
			g = (curr_word, make_guess(curr_word, target))
			print("\tChosen guess: {} {}".format(curr_word.upper(), g))
			wordlist = filter_wordlist(wordlist, g)
			rnd+=1

def parse_guess(st):
	word, pattern = st.split(" ")
	word = word.lower()
	pattern = pattern.upper()
	def to_arr(x):
		for l in x:
			if l=="B": return B
			if l=="G": return G
			if l=="Y": return Y
	pattern = list(map(to_arr, pattern))
	return (word, pattern)


def assist_mode():
	print("input guesses (format \"guess BGYBB\") - Enter again to finish: ")
	guesses = []
	line = input()
	while(line != ""):
		guesses.append(parse_guess(line))
		line = input()
	with open("./wordlist.json") as wordfile:
		words = json.load(wordfile)
		wordlist = words.copy()
		for i, g in enumerate(guesses):
			wordlist = filter_wordlist(wordlist, g)
		print("Possible words: {}/{}".format(len(wordlist), len(words)))
		dynamic_recommend(wordlist)

if __name__ == "__main__":
	print("Select mode:")
	print("1. Analyze mode")
	print("2. AI mode")
	print("3. Assist mode")
	mode = input()
	if mode == "1":
		analyze_mode()
	if mode == "2":
		ai_mode()
	if mode == "3":
		assist_mode()