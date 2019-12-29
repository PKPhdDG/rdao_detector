#include <main.h>

int main()
{
    pthread_t t1;
    pthread_create(&t1, NULL, tread, NULL);
    pthread_join(t1, NULL);
    return 0;
}
