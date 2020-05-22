#include <stdio.h>
#include <pthread.h>

struct human_t {
    char name[32];
    unsigned int age;
};

struct human_t human = {"Damian", 30};

void* change_age(void *args) {
    human.age += 1;
    return NULL;
}

int main() {
    pthread_t t1, t2;
    printf("Start age = %d\r\n", human.age);

    pthread_create(&t1, NULL, change_age, NULL);
    pthread_create(&t2, NULL, change_age, NULL);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    printf("End age = %d\r\n", human.age);
    return 0;
}
