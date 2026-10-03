# Retrieval (RAG) in one note

Information lives in three places: the model's weights (frozen, with a knowledge cutoff), the
context of the current request, and outside the model in files and databases.
Retrieval means choosing what to move from the third place into the second, for this request only.
Nothing the application sends is learned by the model.
