#include <threads.h>

static const unsigned short suffix = 5;
volatile unsigned long shared_variable = 0;
pthread_mutex_t m;

static size_t random()
{
	return 4;  // Programmers love random number 4 ;)
}

void *thread_test(void *args)
{
    for (size_t j = random(); shared_variable < suffix && j < j + suffix; ++j)
    {
		pthread_mutex_lock(&m);
        shared_variable += 1;
		pthread_mutex_unlock(&m);
    }
    return (void*)NULL;
}
