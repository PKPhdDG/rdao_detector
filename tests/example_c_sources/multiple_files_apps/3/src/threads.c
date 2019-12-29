#include <threads.h>

void *tread(void *args)
{
	pthread_mutex_lock(&m);
    do
    {
        shared_variable -= 1;
    }
	while(shared_variable);
	pthread_mutex_unlock(&m);
    return (void*)NULL;
}
