from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
import requests
import openai
import json
from openai import OpenAI
from .models import GithubUser, GithubStats, GeneratedArt
from .serializers import GithubUserSerializer, GithubStatsSerializer, GeneratedArtSerializer

class GithubService:
    def __init__(self, token):
        self.token = token
        self.headers = {'Authorization': f'token {token}'}
        self.base_url = 'https://api.github.com'

    def get_user_info(self, username):
        response = requests.get(
            f'{self.base_url}/users/{username}',
            headers=self.headers
        )
        return response.json()

    def get_user_repos(self, username):
        all_repos = []
        page = 1

        while True:
            response = requests.get(
                f'{self.base_url}/users/{username}/repos',
                headers=self.headers,
                params={'page': page, 'per_page': 100}  # Fetch up to 100 repos per page
            )
            repos = response.json()
            
            if not repos:  # Stop when no more repositories are returned
                break

            all_repos.extend(repos)
            page += 1

        return all_repos
    # def get_repos_updated_in_2024(self, username):
    #     all_repos = self.get_user_repos(username)
    #     repos_in_2024 = [
    #         repo for repo in all_repos
    #         if "2024" in repo['pushed_at']
    #     ]
    #     return repos_in_2024


    def get_user_commits(self, username):
        # Note: This is a simplified version. GitHub API has rate limits
        # and requires pagination for complete data
        response = requests.get(
            f'{self.base_url}/search/commits?q=author:{username}',
            headers={**self.headers, 'Accept': 'application/vnd.github.cloak-preview'}
        )
        return response.json()
    # def get_user_commits_2024(self, username):
    #     query = f"author:{username} committer-date:2024-01-01..2024-12-31"
    #     response = requests.get(
    #         f'{self.base_url}/search/commits',
    #         headers={**self.headers, 'Accept': 'application/vnd.github.cloak-preview'},
    #         params={'q': query}
    #     )
    #     return response.json()

class OpenAIService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client =  OpenAI(
                    api_key=api_key,  
                )

    def generate_prompt(self, stat_name, stat_value):
        try:
            # print(settings.OPENAI_API_KEY)
            response = self.client.chat.completions.create(
                model="gpt-4",  # Use `gpt-3.5-turbo` if you lack access to `gpt-4`
                messages=[
                    {"role": "system", "content": "You are an AI generating prompts for stunning visual designs."},
                    {"role": "user",  "content": f"Create a detailed, visually inspiring prompt for generating a DALL·E image based on the following GitHub stat: "
                                                f"'{stat_name}' with a value of {stat_value}. "
                                                "The prompt should include vibrant imagery, modern icons, a rich color palette, and elements that symbolize the magnitude of the number. "
                                                "The design should be motivational and suitable for sharing on LinkedIn and Instagram."
                    }
                ]
            )
            print(response.choices[0].message.content)
        except Exception as e:
            print("Error:", e)
            print("Falling back to gpt-3.5-turbo...")
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI generating prompts for stunning visual designs."},
                     {"role": "user",  "content": f"Create a detailed, visually inspiring prompt for generating a DALL·E image based on the following GitHub stat: "
                                                f"'{stat_name}' with a value of {stat_value}. "
                                                "The prompt should include vibrant imagery, modern icons, a rich color palette, and elements that symbolize the magnitude of the number. "
                                                "The design should be motivational and suitable for sharing on LinkedIn and Instagram. Prompt length must be below 1000 words."
                    }
                   ]
            )
        print(response)
        return response.choices[0].message.content

    def generate_quote(self, stat_name, stat_value, prompt):
        try:
            # print(settings.OPENAI_API_KEY)
            response = self.client.chat.completions.create(
                model="gpt-4",  # Use `gpt-3.5-turbo` if you lack access to `gpt-4`
                messages=[
                     {"role": "system", "content": "You are an AI specialized in creating motivational and inspiring quotes for achievements."},
                        {
                            "role": "user",
                            "content": (
                                f"Write an inspiring and motivational quote based on this GitHub stat: '{stat_name}' with a value of {stat_value}. "
                                "The quote should emphasize growth, creativity, and impact, and should resonate with developers and tech enthusiasts. Keep in mind that the design is already made with this prompt {prompt}. "
                                "Give a short quotation that will be displayed on the image."
                                "The quote should help the viewer to understand the significance of the stat and inspire them to achieve more."
                            ),
                        },
                ]
            )
            print(response.choices[0].message.content)
        except Exception as e:
            print("Error:", e)
            print("Falling back to gpt-3.5-turbo...")
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI specialized in creating motivational and inspiring quotes for achievements."},
                    {
                        "role": "user",
                        "content": (
                            f"Write an inspiring and motivational quote based on this GitHub stat: '{stat_name}' with a value of {stat_value}. "
                            "The quote should emphasize growth, creativity, and impact, and should resonate with developers and tech enthusiasts."
                        ),
                    },
                   ]
            )
        return response.choices[0].message.content

    def generate_image(self, prompt):
        response = self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        return response.data[0].url

@api_view(['POST'])
def generate_github_wrapped(request):
    username = request.data.get('username')
    print(username)
    if not username:
        return Response(
            {'error': 'Username is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if GithubUser.objects.filter(username=username).exists() and GithubStats.objects.filter(user__username=username).exists():
        return Response({
            'user':  GithubUserSerializer(GithubUser.objects.get(username=username)).data,
            'stats': GithubStatsSerializer(GithubStats.objects.filter(user__username=username).first()).data,
            'generated_art': GeneratedArtSerializer(GeneratedArt.objects.filter(stats__user__username=username), many=True).data
        })

    github_service = GithubService(settings.GITHUB_TOKEN)
    openai_service = OpenAIService(settings.OPENAI_API_KEY)
    try:
        # Get or create GitHub user
        user_info = github_service.get_user_info(username)
        github_user, _ = GithubUser.objects.get_or_create(
            username=username,
            defaults={
                'avatar_url': user_info.get('avatar_url'),
                'name': user_info.get('name'),
                'bio': user_info.get('bio')
            }
        )

        # Collect GitHub stats
        try:
            # Fetch repositories and commits for the user
            repos = github_service.get_user_repos(username)
            commits = github_service.get_user_commits(username)

            # Prepare data to be written to the file
            data = {
                "repositories": repos,
                "commits": commits,
                "user": user_info
            }
            # file_path = "data.json"
            # # Write data to the file in JSON format
            # with open(file_path, "w") as file:
            #     json.dump(data, file, indent=4)

            # print(f"Data successfully written to {file_path}")
        except Exception as e:
            print(f"An error occurred: {e}")
        # print(repos, commits)
        # Create stats object
        stats = GithubStats.objects.create(
            user=github_user,
            total_commits=commits.get('total_count', 0),
            total_repos=len(repos),
            stars_received=sum(repo['stargazers_count'] for repo in repos),
            contributions=sum(repo['size'] for repo in repos),  # Simplified metric
            collobrators = user_info.get('collaborators'),
            followers = user_info.get('followers'),
            most_used_language=max(
                (repo['language'] for repo in repos if repo['language']),
                key=lambda x: sum(1 for r in repos if r['language'] == x),
                default=None
            )
        )

        # Generate art for each stat
        generated_art = []
        for stat_name, stat_value in {
            'Total Commits': stats.total_commits,
            'Total Repositories': stats.total_repos,
            'Stars Received': stats.stars_received,
            'Most Used Language': stats.most_used_language,
            'Contributions': stats.contributions,
            'Collaborators': stats.collobrators,
            'Followers': stats.followers
        }.items():
            prompt = openai_service.generate_prompt(stat_name, stat_value)
            image_url = openai_service.generate_image(prompt)
            quotation = openai_service.generate_quote(stat_name, stat_value, prompt)
            art = GeneratedArt.objects.create(
                stats=stats,
                stat_name=stat_name,
                stat_value=str(stat_value),
                prompt=prompt,
                image_url=image_url,
                quotation=quotation
            )
            generated_art.append(GeneratedArtSerializer(art).data)
        return Response({
            'user': GithubUserSerializer(github_user).data,
            'stats': GithubStatsSerializer(stats).data,
            'generated_art': generated_art
        })

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )