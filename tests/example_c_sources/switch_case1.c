#include <stdio.h>

int main()
{
    int user_choice;
    scanf("%d", &user_choice);
    switch(user_choice)
    {
        case 0:
            printf("You choosed 0!\n");
            break;
        case 1:
            printf("You choosed 1!\n");
    }

    printf("Thank you my user!");
    return 0;
}
