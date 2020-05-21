#include <stdio.h>

typedef struct {
    char name[32];
    unsigned int age;
} human_t;

int main()
{
    human_t human = {"Damian", 30};
    printf("%s: %d", human.name, human.age);
    return 0;
}
