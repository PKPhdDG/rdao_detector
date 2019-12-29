#include <threads.h>
#include <stddef.h>

void *t2f(void *args)
{
	pthread_mutex_lock(&m);
	shared_variable += 1;
	pthread_mutex_unlock(&m);
    return (void*)NULL;
}

void *t1f(void *args)
{
	pthread_mutex_lock(&m);
	shared_variable += 1;
	pthread_mutex_unlock(&m);
    return (void*)NULL;
}
