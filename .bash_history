git clone https://github.com/zee467/stage-3-hng.git
sudo apt install git
git clone https://github.com/zee467/stage-3-hng.git
ls
cd stage-3-hng
ls
docker
sudo apt install docker
docker
sudo apt update
sudo apt upgrade -y
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common gnupg lsb-release
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
docker --version
docker compose version
sudo usermod -aG docker $USER
# Log out and back in to apply
sudo apt install -y nginx
sudo systemctl enable nginx
sudo systemctl start nginx
sudo systemctl status nginx
docker compose up -d
ls
cp .env.example .env
nano .env
docker compose up -d --build
curl -X POST http://localhost:8081/chaos/start?mode=error
python3 watcher.py
ls
cd stage-3-hng
git remote add origin https://github.com/beekyynd/hng13-stage3-devops.git
git branch -M main
git push -u origin main
git remove origin
git remote remove origin
git remote add origin https://github.com/beekyynd/hng13-stage3-devops.git
git branch -M main
git push -u origin main
docker compose ps
nano .env
docker compose down
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/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
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/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
docker compose up -d
nano docker-compose.yml
nano watcher.py
git add .
git commit -m "changes1"
git config --global user.email "you@example.com"
git commit -m "changes1"
git push
nano .gitignore
git rm cached .env
git cached rm .env
git rm -r cached .env
git add .
git commit -m "changes"
git push
git rm --cached .env
git commit -m "changes"
git push
git status
git rm --cached .env
git add .
git commit -m "changes1"
git push
git rm --cached .env
git reset HEAD~1
git rm --cached .env
git add .
git commit -m "Remove .env from Git tracking"
git push
git rm --cached .env
git reset HEAD~1
git rm --cached .env
git add .
git commit -m "Remove .env from Git tracking"
# Install BFG (if not already)
# java -jar bfg.jar --delete-files .env
# OR using git filter-branch
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch .env" --prune-empty --tag-name-filter cat -- --all
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Add .env to .gitignore"
git push origin main --force
nano .env
git add .
git commit -m "changes"
git push
git rm --cached .env
git reset HEAD~1
git rm --cached .env
cd ..
sudo rm stage-3-hng
sudo rm -r stage-3-hng
ls
