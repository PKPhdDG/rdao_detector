#include <stdio.h>

int main()
{
    int user_choice;
    scanf("%d", &user_choice);
    switch(user_choice)
    {
        case 0: {
            printf("You choose 0!\n");
            break;
        }
        case 1:
        case 2:
        case 3:
        case 4:
        case 5:
        case 6:
        case 7:
        case 8:
        case 9:
            printf("You choose positive number less than 10!\n");
            break;
        default:
            switch(user_choice)
            {
                case 10:
                    printf("You choose 10!\n");
                default: {
                    printf("You are in nested switch!\n");
                }
            }
    }

    printf("Thank you my user!\n");
    return 0;
}
