from sys import stderr

from database import addQuote


def writeEpisodeToDb(episode):
    for quote in episode.quotes:
       addQuote(quote.to_tuple())


def writeToDatabase(queue, eps_count):
    '''
    Write <eps_count> episodes in the queue to a database.
    '''
    successful = 0
    while eps_count > 0 or not queue.empty():
        try:
            episode = queue.get()
            if episode:
                writeEpisodeToDb(episode)
                successful += 1
                print("Stored {} episodes successfully;".format(successful), end=" ")
        except Exception as e:
            print("writeToDatabase failed with:\n{}".format(e), file=stderr)
        finally:
            eps_count -= 1
            print("{} episodes remaining".format(eps_count), end=" "*4 + "\r")

    return successful
