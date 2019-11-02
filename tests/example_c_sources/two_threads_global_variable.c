#include <pthread.h>

int shared_variable = 0;
pthread_mutex_t m;

void *t2(void *args)
{
	pthread_mutex_lock(&m);
	shared_variable += 1;
	pthread_mutex_unlock(&m);
    return (void*)NULL;
}

void *t1(void *args)
{
	pthread_mutex_lock(&m);
	shared_variable += 1;
	pthread_mutex_unlock(&m);
    return (void*)NULL;
}

int main()
{
    pthread_t t1, t2;
    pthread_create(&t1, NULL, t1, NULL);
    pthread_create(&t2, NULL, t2, NULL);
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    return 0;
}
