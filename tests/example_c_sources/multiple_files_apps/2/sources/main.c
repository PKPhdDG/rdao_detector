#include <main.h>

int main()
{
    pthread_t t1, t2;
    pthread_create(&t1, NULL, t1f, NULL);
    pthread_create(&t2, NULL, t2f, NULL);
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    return 0;
}
