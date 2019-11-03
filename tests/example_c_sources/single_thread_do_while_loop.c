#include <pthread.h>

int shared_variable = 100;
pthread_mutex_t m;

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

int main()
{
    pthread_t t1;
    pthread_create(&t1, NULL, tread, NULL);
    pthread_join(t1, NULL);
    return 0;
}
