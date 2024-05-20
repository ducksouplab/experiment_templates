import math
from pprint import pprint

PAIRING_2 = [
  [[1, 2]]
]

PAIRING_4 = [
  [[1, 2], [3, 4]],
  [[1, 3], [2, 4]],
  [[1, 4], [2, 3]]
]

PAIRING_6 = [
  [[1, 2], [3, 4], [5, 6]],
  [[1, 3], [2, 5], [4, 6]],
  [[1, 4], [2, 6], [3, 5]],
  [[1, 5], [2, 4], [3, 6]]
]

PAIRING_8 = [
  [[1, 2], [3, 4], [5, 6], [7, 8]],
  [[1, 3], [2, 5], [4, 7], [6, 8]],
  [[1, 4], [2, 6], [3, 7], [5, 8]],
  [[1, 5], [2, 7], [3, 6], [4, 8]]
]

PAIRING_10 = [
  [[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]],
  [[1, 10], [2, 3], [4, 5], [6, 7], [8, 9]],
  [[1, 3], [2, 6], [7, 10], [4, 9], [5, 8]],
  [[1, 5], [2, 7], [3, 9], [4, 8], [6, 10]]
]

PAIRING_12 = [
  [[1, 2], [3, 4], [5, 6], [7, 8], [9, 10], [11, 12]],
  [[1, 12], [2, 3], [4, 5], [6, 7], [8, 9], [10, 11]],
  [[1, 8], [2, 7], [3, 12], [4, 9], [5, 10], [6, 11]],
  [[1, 7], [2, 8], [3, 9], [4, 10], [5, 11], [6, 12]]
]

PAIRING_14 = [
  [[1, 2]  , [3, 4] , [5, 6]  , [7, 8]   , [9, 10] , [11, 12], [13, 14]],
  [[1, 12] , [2, 3] , [4, 5]  , [6, 7]   , [8, 9]  , [10, 14], [11, 13]],
  [[1, 8]  , [2, 7] , [3, 12] , [4, 11]  , [5, 10] , [6, 14] , [9, 13]],
  [[11, 7] , [2, 8] , [3, 9]  , [4, 10]  , [5, 14] , [6, 12] , [1, 13]]
  ]

# custom rule, with 1 to 4 rounds
def get_all_pairs_size_2_to_8(num_participants, round_number):
  if num_participants == 2: return PAIRING_2[round_number - 1]
  if num_participants == 4: return PAIRING_4[round_number - 1]
  if num_participants == 6: return PAIRING_6[round_number - 1]
  if num_participants == 8: return PAIRING_8[round_number - 1]


# custom rule, with 1 to 4 rounds
def get_all_pairs_size_2_to_14(num_participants, round_number):
  if num_participants == 2: return PAIRING_2[round_number - 1]
  if num_participants == 4: return PAIRING_4[round_number - 1]
  if num_participants == 6: return PAIRING_6[round_number - 1]
  if num_participants == 8: return PAIRING_8[round_number - 1]
  if num_participants == 10: return PAIRING_10[round_number - 1]
  if num_participants == 12: return PAIRING_12[round_number - 1]
  if num_participants == 14: return PAIRING_14[round_number - 1]

# the first half of players interacts with the other half, for a 8 participants session:
# - player 1 will interact with 5, 6, 7, 8
# - player 2 will interact with 6, 7, 8, 5...
def pair_with_other_half(num_participants, round_number):
  num_rounds = math.floor(num_participants/2)
  round_index = round_number - 1

  pairs = []
  for id in range(1, num_rounds + 1):
    other_id = (id + round_index) % num_rounds
    if other_id == 0:
      other_id = num_rounds
    other_id += num_rounds
    pairs.append([id, other_id])
  return pairs