"""

CSE 535 Information Retrieval Fall 2019 Project 2
Boolean Query and Inverted Index

Name: Srisai Karthik Neelamraju
UBID: 50316785
UBIT: neelamra

"""

import sys

class Posting:
    """
       class defining a posting in the inverted index
    """
    def __init__(self, docID):
        """
           creates a posting
           arguments -
                (1) docID (int): document ID of the posting to be created
        """
        self.docID = docID                      # document ID
        self.tf = 1                             # term frequency in the document
        self.next = None                        # pointer to the next posting


class PostingsList:
    """
       class defining a postings list in the inverted index, implemented as a linked list
    """
    def __init__(self, docID):
        """
           creates a postings list
           arguments -
                (1) docID (int): document ID of the first posting in the postings list
        """
        self.head = Posting(docID)              # first posting of the list
        self.tail = self.head                   # last posting of the list
        self.df = 1                             # document frequency of the term

    def add_posting(self, docID):
        """
           adds a posting to the postings list
           arguments -
                (1) docID (int): document ID of the posting to be added
        """
        posting = Posting(docID)
        self.tail.next = posting
        self.tail = posting
        self.df += 1
        return

    def get_posting(self, docID):
        """
           finds a posting in the postings list
           arguments -
                (1) docID (int): document ID of the posting to be searched
           returns -
                (1) curr (Posting): if the posting is present and None: if it is not
        """
        curr = self.head
        if curr is None:
            return None
        while curr is not None:
            if curr.docID == docID:
                return curr
            curr = curr.next
        return None

    def sort_postings(self):
        """
           sorts the postings list in increasing order of document IDs
           returns -
                (1) _ (PostingsList): the sorted postings list
        """
        if self.head is None:
            return
        sorted_idx = None
        while sorted_idx != self.head:
            curr = self.head
            while curr.next != sorted_idx:
                nxt = curr.next
                if curr.docID > nxt.docID:
                    temp = curr.docID
                    curr.docID = nxt.docID
                    nxt.docID = temp
                curr = curr.next
            sorted_idx = curr
        return self


def build_inverted_index(collection):
    """
       constructs an inverted index as a python dictionary from the input corpus
       arguments -
            (1) collection (nested list): list of [document ID, document text]
       returns -
            (1) index (dict): inverted index with terms as keys and corresponding postings lists as values
    """
    # initializing the inverted index
    index = {}

    for doc in collection:

        # document ID
        docID = int(doc[0])

        # white space tokenized document text
        terms = doc[1].split(" ")

        # building the postings list for each term
        for term in terms:

            # check if the term is present in the index
            if term not in index:

                # create a new postings list for the term and add the document
                index[term] = PostingsList(docID)

            else:
                # retrieve the postings list of the term
                postings_list = index[term]

                # retrieve the posting with this document ID
                posting = postings_list.get_posting(docID)

                # check if such posting is indeed present in the postings list
                if posting is None:

                    # add a new posting with this document ID to the postings list
                    postings_list.add_posting(docID)

                else:
                    # increase the term frequency
                    posting.tf += 1

    # returning the inverted index
    return index


def get_postings(terms, index, output_fpath):
    """
       writes respective postings of terms in the increasing order of their document IDs
       arguments -
            (1) terms (list): list of terms whose postings are to be retrieved
            (2) index (dict): inverted index
            (3) output_fpath (str): path of the output file
    """
    for term in terms:

        # retrieving postings of term
        postings = index[term]

        # creating a string of document IDs
        postings_str = ""
        curr = postings.head
        while curr.next is not None:
            postings_str += str(curr.docID) + " "
            curr = curr.next
        postings_str += str(curr.docID)

        # writing to the output file
        with open(output_fpath, "a") as out:
            out.write("GetPostings\n" + term + "\nPostings list: " + postings_str + "\n")


def daat_AND(terms, index, output_fpath):
    """
       implements multi-term boolean AND query using document-at-a-time strategy
       arguments -
            (1) terms (list): list of terms in the boolean query
            (2) index (dict): inverted index
            (3) output_fpath (str): path of the output file
       returns -
            (1) results (list): list of document IDs satisfying the query
    """
    results = []
    n_comp = 0
    n_matched = 0

    # retrieving all postings lists at a time
    postings_list_arr = [index[term] for term in terms]

    # keeping pointers to each of the posting lists in a separate list
    ptrs = [postings_list.head for postings_list in postings_list_arr]

    # document-at-a-time AND query implementation
    while True:

        # add all postings to the results when only there is one query term
        if len(ptrs) == 1:
            curr = ptrs[0]
            while curr != None:
                results.append(curr.docID)
                curr = curr.next
            # finish processing
            break

        try:
            for i in range(1, len(ptrs)):

                # update the pointer to the postings list with smaller docID
                if ptrs[0].docID < ptrs[i].docID:
                    ptrs[0] = ptrs[0].next
                elif ptrs[0].docID > ptrs[i].docID:
                    ptrs[i] = ptrs[i].next
                else:
                    n_matched += 1

                # increment the number of comparisons
                n_comp += 1

            # add to results if current document IDs in each of the postings lists match
            if n_matched == len(ptrs) - 1:
                results.append(ptrs[i].docID)
                ptrs = [ptr.next for ptr in ptrs]
            n_matched = 0

        except:
            # finish processing when the first null pointer exception occurs
            break

    # creating a string of query terms
    terms_str = ""
    for term in terms[:-1]:
        terms_str += term + " "
    terms_str += terms[-1]

    # creating a string of result document IDs
    results_str = ""
    if len(results) > 0:
        for result in results[:-1]:
            results_str += str(result) + " "
        results_str += str(results[-1])
    else:
        results_str = "empty"

    # writing to the output file
    with open(output_fpath, "a") as out:
        out.write("DaatAnd\n" + terms_str + "\nResults: " + results_str + "\nNumber of documents in results: " + str(len(results)) + "\nNumber of comparisons: " + str(n_comp) + "\n")
    
    # returning the document IDs satisfying the boolean AND query
    return results


def daat_OR(terms, index, output_fpath):
    """
       implements multi-term boolean OR query using document-at-a-time strategy
       arguments -
            (1) terms (list): list of terms in the boolean query
            (2) index (dict): inverted index
            (3) output_fpath (str): path of the output file
       returns -
            (1) results (list): list of document IDs satisfying the query
    """
    results = []
    n_comp = 0

    # retrieving all postings lists at a time
    postings_list_arr = [index[term] for term in terms]
    
    # keeping pointers to each of the posting lists in a separate list
    ptrs = [postings_list.head for postings_list in postings_list_arr]

    # document-at-a-time OR query implementation
    while True:

        # add all postings to the results when only there is one query term
        if len(ptrs) == 1:
            curr = ptrs[0]
            while curr != None:
                results.append(curr.docID)
                curr = curr.next
            # finish processing
            break

        # find the posting(s) with least docID among all the postings lists
        min_docID = ptrs[0].docID
        min_locs = [0]
        for i in range(1, len(ptrs)):
            if ptrs[i].docID < min_docID:
                min_docID = ptrs[i].docID
                del min_locs[:]
                min_locs.append(i)
            elif ptrs[i].docID == min_docID:
                min_locs.append(i)
            
            # increment the number of comparisons
            n_comp += 1

        # add the least docID to the results
        results.append(min_docID)

        # update the pointers to each of the postings with the least docID
        for i in min_locs:
            ptrs[i] = ptrs[i].next

        # check if traversal of any of the postings lists is completed
        finished_lists = []
        for i in range(len(ptrs)):
            if ptrs[i] is None:
                finished_lists.append(i)

        # if so, remove the pointer to the completed postings lists
        for i in sorted(finished_lists, reverse=True):
            del ptrs[i]

        # finish processing if all postings lists have been traversed
        if len(ptrs) == 0:
            break

    # creating a string of query terms
    terms_str = ""
    for term in terms[:-1]:
        terms_str += term + " "
    terms_str += terms[-1]

    # creating a string of result document IDs
    results_str = ""
    if len(results) > 0:
        for result in results[:-1]:
            results_str += str(result) + " "
        results_str += str(results[-1])
    else:
        results_str = "empty"

    # writing to the output file
    with open(output_fpath, "a") as out:
        out.write("DaatOr\n" + terms_str + "\nResults: " + results_str + "\nNumber of documents in results: " + str(len(results)) + "\nNumber of comparisons: " + str(n_comp) + "\n")

    # returning the document IDs satisfying the boolean OR query
    return results


def tf_idf_ranking(query_terms, documents, index, document_lengths, collection_size, output_fpath):
    """
       computes document scores using tf-idf
       arguments -
            (1) query_terms (list): list of terms in the boolean query
            (2) documents (list): list of document IDs satisfying the query
            (3) index (dict): inverted index
            (4) document_lengths (dict): dictionary with document IDs as keys and number of terms in them as values
            (5) collection_size (int): number of documents in the corpus
            (6) output_fpath (str): path of the output file
       returns -
            (1) results (list): list of documents sorted using tf-idf scores
    """
    # initializing tf-idf score for each document to zero
    tf_idf = [0 for _ in range(len(documents))]

    # evaluating tf-idf score for each document
    for i in range(len(documents)):
        for term in query_terms:
            posting = index[term].get_posting(documents[i])
            if posting is not None:
                tf = float(posting.tf)/document_lengths[posting.docID]
                idf = float(collection_size)/index[term].df
                tf_idf[i] += tf * idf

    # sorting documents based on the tf-idf scores
    results = [docID for _, docID in sorted(zip(tf_idf, documents), key=lambda x: (-x[0], x[1]))]

    # creating a string of result document IDs
    results_str = ""
    if len(results) > 0:
        for result in results[:-1]:
            results_str += str(result) + " "
        results_str += str(results[-1])
    else:
        results_str = "empty"

    # writing to the output file
    with open(output_fpath, "a") as out:
        out.write("TF-IDF\nResults: " + results_str + "\n")


def parse_args():
    """
       parses the command line arguments
       returns -
            (1) args (dict): dictionary with paths lo the input corpus, output and input files;
            has three keys - "corpus_fpath", "output_fpath" and "input_fpath"
    """
    args = {}
    args["corpus_fpath"] = sys.argv[1]
    args["output_fpath"] = sys.argv[2]
    with open(args["output_fpath"], "w") as out:
        out.close()
    args["input_fpath"] = sys.argv[3]
    return args


def main_func():
    """
       main function for the project 2 implementation
    """
    # parsing the command line arguments
    args = parse_args()

    # reading documents from the input corpus
    with open(args["corpus_fpath"], "r") as corpus:
       collection = [doc.strip("\n").split("\t") for doc in corpus]

    # building the inverted index
    index = build_inverted_index(collection)

    # fetching the query terms from the input file
    with open(args["input_fpath"], "r") as inp:
        split_queries = [query.split() for query in inp]

    # finding parameters required for computing tf-idf scores -

    # (1) number of documents in the collection
    collection_size = len(collection)

    # (2) number of terms in each document
    document_lengths = {}
    for doc in collection:
        docID = int(doc[0])
        terms = doc[1].split(" ")
        document_lengths[docID] = len(terms)

    # implementing all the required procedures
    for i in range(len(split_queries)):

        # query terms in a list
        query_terms = split_queries[i]

        # get postings lists
        get_postings(query_terms, index, args["output_fpath"])

        # document-at-a-time AND query
        results_AND = daat_AND(query_terms, index, args["output_fpath"])

        # ranking results obtained from daat_AND using tf-idf scores
        tf_idf_ranking(query_terms, results_AND, index, document_lengths, collection_size, args["output_fpath"])

        # document-at-a-time OR query
        results_OR = daat_OR(query_terms, index, args["output_fpath"])

        # ranking results obtained from daat_OR using tf-idf scores
        tf_idf_ranking(query_terms, results_OR, index, document_lengths, collection_size, args["output_fpath"])

        if i < len(split_queries) - 1:
            with open(args["output_fpath"], "a") as out:
                out.write("\n")


if __name__ == "__main__":
    main_func()
