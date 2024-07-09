import pandas as pd
import numpy as np
from rapidfuzz import fuzz, process, distance
import preprocessing


class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [1] * n

    def find(self, u):
        if self.parent[u] != u:
            self.parent[u] = self.find(self.parent[u])
        return self.parent[u]

    def union(self, u, v):
        root_u = self.find(u)
        root_v = self.find(v)
        if root_u != root_v:
            if self.rank[root_u] > self.rank[root_v]:
                self.parent[root_v] = root_u
            elif self.rank[root_u] < self.rank[root_v]:
                self.parent[root_u] = root_v
            else:
                self.parent[root_v] = root_u
                self.rank[root_u] += 1

def similar_words(strings):

    n = len(strings)
    if n < 3:
        return strings
    else:
        pairwise_similarities = np.zeros((n, n))
        for i, s1 in enumerate(strings):
            for j, s2 in enumerate(strings):
                pairwise_similarities[i, j] = distance.DamerauLevenshtein.normalized_similarity(s1, s2)

            # Initialize Union-Find structure
        uf = UnionFind(n)
        threshold = 0.7
        # Union sets based on the threshold
        for i in range(n):
            for j in range(i + 1, n):
                if pairwise_similarities[i][j] >= threshold:
                    uf.union(i, j)

        # Group strings based on connected components
        groups = {}
        for i in range(n):
            root = uf.find(i)
            if root not in groups:
                groups[root] = []
            groups[root].append(strings[i])

        return list(groups.values())


def FuzzyMatching(skills, jobd):

    # -------------------------------------------------------- DATA PREPARATION ----------------------------------------------------------- #

    # SKILLS DATAFRAME
    pd_skills = pd.DataFrame(skills)

    # SENTENCES DATAFRAME
    sentences = preprocessing.tokenize_sentences(jobd)
    sentences_pp = []
    for i in range(len(sentences)):
        sentences_pp.append(preprocessing.lemmatization(preprocessing.preprocessing(sentences[i])))
    pd_sentences = pd.DataFrame({'sentences':sentences_pp})

    # -------------------------------------------------------- SKILLS EXTRACTION ----------------------------------------------------------- #

    # PRE-SELECTION: Keep only potential extracted skills 
    pd_skills = pd_skills[pd_skills['lemma'].apply(lambda x: fuzz.partial_token_set_ratio(x, ''.join(sentences_pp)) > 60)]
    # print(pd_skills)
    def treat(skills_row):
        def calculate_score(sentence_row):
            if fuzz.partial_token_set_ratio(skills_row['lemma'], sentence_row['sentences']) < 50:
                return (skills_row['full'], skills_row['type'], 0)
            score = 0
            tokens = skills_row['lemma'].split()
            for t1 in tokens:
                t2 = process.extractOne(t1, sentence_row['sentences'].split(), scorer=distance.DamerauLevenshtein.normalized_similarity)
                if t2 is not None and t2[1] > 0.9:
                    score += t2[1]
                elif t2[1] < 0.9:
                    if len(tokens) < 3:
                        return (skills_row['full'], skills_row['type'], 0)
                    else:
                        score += t2[1]

    # drop if score low
            if len(tokens) > 0:
                score /= len(tokens)
            return (skills_row['full'], skills_row['type'], score)

        return pd_sentences.apply(calculate_score, axis=1)

    pd_scores = pd_skills.apply(treat, axis=1)

    filtered_df = pd_scores.apply(lambda x: pd.Series({skill_full: {type: score} for skill_full, type, score in x if score > 0.9}))

    # -------------------------------------------------------- SKILLS FILTRATION ----------------------------------------------------------- #

    stacked = filtered_df.stack()

    finalSK = []
    # Display non-null values with their row and column indices
    for index, value in stacked.items():
        skills_extracted = {}
        skills_extracted['full'] = index[0]
        skills_extracted['sent'] = index[1]
        skills_extracted['score'] = list(value.values())[0] - 0.15
        skills_extracted['type'] = list(value.keys())[0]
        finalSK.append(skills_extracted)

    skills_extracted_df = pd.DataFrame(finalSK)
    if not skills_extracted_df.empty:

        hello = pd.DataFrame(skills_extracted_df.groupby('sent')['full'].agg(list))

        # Eliminate false positive skills
        maplist = []
        for index, row in hello.iterrows():
            groups = similar_words(row['full'])
            if len(row['full']) == len(groups):
                continue
            for group in groups:
                if len(group) == 1:
                    continue
                group.remove(process.extractOne(sentences[index], group, scorer=distance.DamerauLevenshtein.normalized_similarity)[0])
                if group is not None:
                    maplist.extend(list(map(lambda x: (x, index), group)))

        # Create a DataFrame from skill_sent_list
        df_skill_sent = pd.DataFrame(maplist, columns=['full', 'sent'])
        # Filter out rows in df based on skill_sent_list
        skills_extracted_df = skills_extracted_df[~skills_extracted_df[['full', 'sent']].apply(tuple, axis=1).isin(df_skill_sent.apply(tuple, axis=1))]
        # Remove redundant skills and keep the best score
        return skills_extracted_df.loc[skills_extracted_df.groupby('full')['score'].idxmax()]
    else:
        return skills_extracted_df