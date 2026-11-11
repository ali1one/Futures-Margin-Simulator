"""All the text of the web page, in English and in French.

Every language has the same keys (a test checks it). Texts with {words} in
curly braces are templates: the page fills the {words} in with numbers.
The page picks a language with ?lang=fr (English is the default).
"""

EN = {
    "locale": "en-US",
    "money": "${n}",          # how a dollar amount is written
    "percent": "{n}%",        # how a percentage is written

    # ----- page -----
    "title": "Index futures: daily settlement and margin calls",
    "description": "Interactive simulator to understand daily settlement of a future, "
                   "margin calls, and the effect of correlation with interest rates.",
    "lead": "Why is a future worth slightly more than a forward when the index is positively "
            "correlated with interest rates? Run the simulation to see it.",
    "noscript": "This page needs JavaScript to work.",

    # ----- guide -----
    "guide_title": "How it works in 5 steps",
    "guide": [
        "<strong>A future</strong> is an agreement signed today to buy the S&amp;P 500 index "
        "later, at a price fixed now (here <span data-param='start_price'></span> points). "
        "Each point is worth <span data-param='point_value' data-format='money'></span>.",

        "<strong>Margin.</strong> You pay nothing for the contract itself, but you put up a "
        "<span data-param='start_margin' data-format='money'></span> deposit in an account at "
        "your broker. It isn't the price of the future: it's your own money set aside, like a "
        "rental deposit.",

        "<strong>Daily settlement.</strong> Every day, the exchange settles the accounts. If the "
        "index rises, the buyer's gain is added to the buyer's account (it comes from the seller "
        "on the other side). If it falls, the buyer's loss is taken out and goes to the seller. "
        "A short position is the mirror image.",

        "<strong>Margin call.</strong> If your account falls below "
        "<span data-param='maintenance_margin' data-format='money'></span>, you must deposit cash "
        "to bring it back to <span data-param='start_margin' data-format='money'></span>.",

        "<strong>The interest rate</strong> is the price of money, set by the market and the "
        "central bank (here <span data-param='start_rate' data-format='percent'></span> at the "
        "start). You invest the day's gain at that rate, and you borrow the day's loss at that "
        "rate. If the index and rates move together (positive correlation), the buyer invests "
        "gains at a high rate and finances losses at a low rate. A forward settles nothing "
        "before the end, so it has no such edge. That is why, with a positive correlation, the "
        "future's price sits slightly above the forward's price.",
    ],

    # ----- settings -----
    "settings_title": "Settings",
    "settings_note": "Changing a setting restarts the game.",
    "position_label": "Position",
    "long": "Long (buyer)",
    "short": "Short (seller)",
    "setting_volatility": "Index volatility per step (%)",
    "setting_rate_volatility": "Rate volatility per step (points)",
    "setting_steps": "Steps to maturity",
    "setting_start_margin": "Initial margin ($)",
    "setting_maintenance_ratio": "Margin call level (% of initial margin)",

    # ----- simulation -----
    "sim_title": "Simulation",
    "corr_label": "S&P / rate correlation",
    "corr_positive": "positive",
    "corr_negative": "negative",
    "corr_zero": "near zero",
    "btn_up": "S&P +2%",
    "btn_down": "S&P −2%",
    "btn_random": "Random step",
    "btn_auto": "Play to maturity",
    "btn_undo": "Undo",
    "btn_restart": "Restart",
    "btn_share": "Copy link",
    "btn_csv": "Download CSV",
    "btn_tour": "Guided tour",
    "tile_step": "Step",
    "tile_price": "Futures price",
    "tile_rate": "Interest rate",
    "tile_balance": "Margin account",
    "chart_flows": "Cash flow of each step ($)",
    "chart_rates": "Interest rate (%)",
    "chart_balance": "Margin account ($): red dots are margin calls, dashed line is the call level",
    "aria_flows": "Cash gains and losses at each step of the future",
    "aria_rates": "Interest rate over the steps",
    "aria_balance": "Margin account balance over the steps, with the margin call level",
    "th_step": "Step",
    "th_index": "S&P",
    "th_corr": "Corr.",
    "th_rate": "Rate",
    "th_cash": "Daily cash flow",
    "th_balance": "Margin account",
    "th_interest": "Interest on this flow",
    "no_steps": "No step played yet.",
    "call_tag": "(margin call {amount})",

    # ----- future vs forward -----
    "compare_title": "Future vs forward, in this scenario",
    "box_future": "Future: cash + interest",
    "box_forward": "Forward: settled at the end",
    "box_gap": "Gap (interest)",
    "gap_few": "Play a few steps to see the gap appear.",
    "gap_earned": "In this scenario, daily settlement earned you {amount} more than a forward "
                  "would have, thanks to interest.",
    "gap_cost": "In this scenario, daily settlement cost you {amount} more than a forward "
                "would have, because of interest.",
    "gap_zero": "In this scenario, the gap is almost zero.",

    # ----- Monte Carlo -----
    "mc_title": "And on average? A single scenario is mostly luck",
    "mc_button": "Run 2,000 scenarios",
    "mc_wait": "Calculating…",
    "mc_header": "Average future − forward gap over {paths} scenarios (± margin of error), "
                 "and the same gap as a price difference in index points",
    "mc_neg": "Negative correlation (−1)",
    "mc_zero": "Zero correlation (0)",
    "mc_pos": "Positive correlation (+1)",
    "mc_value": "{average} ± {error} (≈ {points} pts)",
    "mc_note": "How to read it: pts is how far the future's price should sit above (+) or below "
               "(−) the forward's price to make up for the interest effect. It is the same "
               "for the buyer and the seller.",
    "footnote": "Simplification: one step = one settlement, and interest is counted as if a "
                "step lasted one month (rate / 12) so the effect is visible. In reality, "
                "settlement is daily. The size of the gaps depends on the volatility settings "
                "and is only illustrative; their sign depends on the correlation and on your "
                "position. Educational tool, not financial advice.",

    # ----- messages about a step -----
    "intro": "You are {position} one S&P 500 future (1 point = {point}). Initial margin is "
             "{start}: if the account falls below {maintenance}, you must top it up (margin "
             "call). Pick a correlation, then play a step.",
    "position_long": "long",
    "position_short": "short",
    "step_head": "Step {step}: the S&P {direction} {pct}.",
    "rises": "rises",
    "falls": "falls",
    "step_gain": "You gain {amount}, credited to your account right away.",
    "step_loss": "You lose {amount}, debited right away.",
    "rate_flat": "The rate doesn't move ({rate}).",
    "rate_move": "The rate {direction} to {rate}: {action} at a {level} rate, "
                 "which works {verdict}.",
    "action_gain": "you invest this gain",
    "action_loss": "you finance this loss",
    "level_up": "higher",
    "level_down": "lower",
    "verdict_good": "in your favor",
    "verdict_bad": "against you",
    "margin_call": "Account below {maintenance}: margin call, you deposit {amount} to get "
                   "back to {start}.",

    # ----- other messages -----
    "maturity": "Maturity reached. Click “Restart” to play again.",
    "auto_done": "Random scenario played to maturity. See the gap between future and "
                 "forward below.",
    "network_error": "Could not reach the server.",
    "server_error": "Something went wrong.",
    "link_copied": "Link copied to the clipboard.",
    "link_manual": "Copy this link: {url}",

    # ----- guided tour -----
    "tour_stage": "Stage {n} of {total}",
    "tour_next": "Next",
    "tour_finish": "Finish",
    "tour_exit": "Exit tour",
    "tour": [
        {
            "title": "1. You buy a future",
            "text": "You just bought one future on the S&P 500 at {start_price} points. Each "
                    "point is worth {point}, so the contract covers {exposure} of the index. "
                    "You paid nothing for the contract itself: you only put {start} aside in "
                    "your margin account.",
            "question": "Did you pay {exposure} to buy the contract?",
            "options": ["Yes, the full amount", "No, only a deposit (the margin)"],
            "answer": 1,
            "right": "Right. The margin is a deposit that stays yours, not the price of the "
                     "future.",
            "wrong": "Not quite. The margin is only a deposit that stays yours: you did not "
                     "pay for the contract.",
        },
        {
            "title": "2. Daily settlement",
            "text": "The index rises 2%, so the future goes to {price} points. The exchange "
                    "settles right away: {cash} lands in your margin account, taken from the "
                    "seller on the other side.",
            "question": "Where does this gain come from?",
            "options": ["From the seller, through the exchange", "From the central bank",
                        "The exchange creates it"],
            "answer": 0,
            "right": "Yes. For every winner there is a loser: the seller pays, and the "
                     "exchange passes the money on.",
            "wrong": "No. It comes from the seller on the other side, through the exchange.",
        },
        {
            "title": "3. A loss",
            "text": "The index falls 2%. {cash} leaves your account. Your balance is now "
                    "{balance}, still above the margin call level of {maintenance}.",
            "question": "Do you get a margin call now?",
            "options": ["Yes", "No"],
            "answer": 1,
            "right": "Correct: {balance} is above {maintenance}.",
            "wrong": "Not yet: {balance} is still above {maintenance}.",
        },
        {
            "title": "4. The margin call",
            "text": "The index falls again: {cash}. Your balance would drop below "
                    "{maintenance}, so you get a margin call: you deposit {call} to get back "
                    "to {start}.",
            "question": "What does a margin call ask you to do?",
            "options": ["Close the contract immediately", "Deposit cash to top the account back up",
                        "Nothing, it is only a warning"],
            "answer": 1,
            "right": "Yes. It is just a top-up of your deposit.",
            "wrong": "No. You deposit cash to bring the account back to its starting level.",
        },
        {
            "title": "5. Why the correlation matters",
            "text": "The index rises 2%: you gain {cash} and the rate rises to {rate}, so you "
                    "invest this gain at a higher rate. Remember your losses: the rate was "
                    "falling then, so you financed them cheaply.",
            "question": "With a positive correlation, what happens to the interest on your "
                        "gains and losses?",
            "options": ["You earn more on gains and pay less on losses",
                        "You earn less on gains and pay more on losses", "Nothing changes"],
            "answer": 0,
            "right": "Yes. Gains come with high rates, losses come with low rates.",
            "wrong": "No. With a positive correlation, gains come with high rates and losses "
                     "come with low rates.",
        },
        {
            "title": "6. Future vs forward",
            "text": "We play the remaining steps at random. In this scenario the gap between "
                    "the future and the forward is {gap}. One scenario is mostly luck: run "
                    "the 2,000 scenarios below to see the average.",
            "question": "Over many scenarios with a positive correlation, the future is worth "
                        "... the forward (for the buyer).",
            "options": ["slightly more than", "slightly less than", "exactly the same as"],
            "answer": 0,
            "right": "Yes. The buyer earns a little more on gains and pays a little less on "
                     "losses, so the future's price is slightly higher than the forward's.",
            "wrong": "Look at the average over many scenarios: with a positive correlation "
                     "the gap is positive for the buyer.",
        },
    ],
}

FR = {
    "locale": "fr-FR",
    "money": "{n} $",
    "percent": "{n} %",

    "title": "Futures sur indice : règlement quotidien et appel de marge",
    "description": "Simulateur interactif pour comprendre le règlement quotidien d'un future, "
                   "l'appel de marge et l'effet de la corrélation avec les taux d'intérêt.",
    "lead": "Pourquoi un future vaut-il un peu plus qu'un forward quand l'indice est corrélé "
            "positivement aux taux d'intérêt ? Joue la simulation pour le voir.",
    "noscript": "Cette page a besoin de JavaScript pour fonctionner.",

    "guide_title": "Le principe en 5 étapes",
    "guide": [
        "<strong>Un future</strong>, c'est un accord signé aujourd'hui pour acheter l'indice "
        "S&amp;P 500 plus tard, à un prix fixé maintenant (ici "
        "<span data-param='start_price'></span> points). Chaque point vaut "
        "<span data-param='point_value' data-format='money'></span>.",

        "<strong>La marge.</strong> Tu ne paies rien pour le contrat lui-même, mais tu déposes "
        "une garantie de <span data-param='start_margin' data-format='money'></span> sur un "
        "compte chez ton courtier. Ce n'est pas le prix du future : c'est ton argent mis de "
        "côté, comme une caution de location.",

        "<strong>Le règlement quotidien.</strong> Chaque jour, la bourse règle les comptes. Si "
        "l'indice monte, le gain de l'acheteur est ajouté à son compte (il vient du vendeur "
        "d'en face). S'il baisse, la perte de l'acheteur est retirée et va au vendeur. La "
        "position vendeuse est le miroir exact.",

        "<strong>L'appel de marge.</strong> Si ton compte passe sous "
        "<span data-param='maintenance_margin' data-format='money'></span>, tu dois verser du "
        "cash pour revenir à <span data-param='start_margin' data-format='money'></span>.",

        "<strong>Le taux d'intérêt</strong> est le prix de l'argent, fixé par le marché et la "
        "banque centrale (ici <span data-param='start_rate' data-format='percent'></span> au "
        "départ). Le gain du jour, tu le places à ce taux. La perte du jour, tu l'empruntes à "
        "ce taux. Si l'indice et les taux vont dans le même sens (corrélation positive), "
        "l'acheteur place ses gains à un taux haut et finance ses pertes à un taux bas. Le "
        "forward, lui, ne règle rien avant la fin : il n'a pas cet avantage. C'est pourquoi, "
        "avec une corrélation positive, le prix du future est un peu au-dessus de celui du "
        "forward.",
    ],

    "settings_title": "Réglages",
    "settings_note": "Modifier un réglage relance la partie.",
    "position_label": "Position",
    "long": "Acheteur (long)",
    "short": "Vendeur (short)",
    "setting_volatility": "Volatilité de l'indice par étape (%)",
    "setting_rate_volatility": "Volatilité du taux par étape (points)",
    "setting_steps": "Étapes jusqu'à l'échéance",
    "setting_start_margin": "Marge initiale ($)",
    "setting_maintenance_ratio": "Seuil d'appel de marge (% de la marge initiale)",

    "sim_title": "Simulation",
    "corr_label": "Corrélation S&P / taux",
    "corr_positive": "positive",
    "corr_negative": "négative",
    "corr_zero": "quasi nulle",
    "btn_up": "S&P +2 %",
    "btn_down": "S&P −2 %",
    "btn_random": "Étape au hasard",
    "btn_auto": "Jouer jusqu'à l'échéance",
    "btn_undo": "Annuler",
    "btn_restart": "Recommencer",
    "btn_share": "Copier le lien",
    "btn_csv": "Télécharger le CSV",
    "btn_tour": "Visite guidée",
    "tile_step": "Étape",
    "tile_price": "Prix du future",
    "tile_rate": "Taux d'intérêt",
    "tile_balance": "Compte de marge",
    "chart_flows": "Flux de cash de chaque étape ($)",
    "chart_rates": "Taux d'intérêt (%)",
    "chart_balance": "Compte de marge ($) : points rouges = appels de marge, "
                     "pointillés = seuil d'appel",
    "aria_flows": "Gains et pertes de cash à chaque étape du future",
    "aria_rates": "Évolution du taux d'intérêt au fil des étapes",
    "aria_balance": "Solde du compte de marge au fil des étapes, avec le seuil d'appel de marge",
    "th_step": "Étape",
    "th_index": "S&P",
    "th_corr": "Corr.",
    "th_rate": "Taux",
    "th_cash": "Flux du jour",
    "th_balance": "Compte de marge",
    "th_interest": "Intérêts sur ce flux",
    "no_steps": "Aucune étape jouée.",
    "call_tag": "(appel de marge {amount})",

    "compare_title": "Future contre forward, sur ce scénario",
    "box_future": "Future : cash + intérêts",
    "box_forward": "Forward : réglé à la fin",
    "box_gap": "Écart (intérêts)",
    "gap_few": "Joue quelques étapes pour voir apparaître l'écart.",
    "gap_earned": "Sur ce scénario, le règlement quotidien t'a rapporté {amount} de plus "
                  "qu'un forward, grâce aux intérêts.",
    "gap_cost": "Sur ce scénario, le règlement quotidien t'a coûté {amount} de plus "
                "qu'un forward, à cause des intérêts.",
    "gap_zero": "Sur ce scénario, l'écart est quasi nul.",

    "mc_title": "Et en moyenne ? Un seul scénario dépend du hasard",
    "mc_button": "Lancer 2 000 scénarios",
    "mc_wait": "Calcul en cours…",
    "mc_header": "Écart moyen future − forward sur {paths} scénarios (± marge d'erreur), "
                 "et le même écart exprimé en différence de prix en points d'indice",
    "mc_neg": "Corrélation négative (−1)",
    "mc_zero": "Corrélation nulle (0)",
    "mc_pos": "Corrélation positive (+1)",
    "mc_value": "{average} ± {error} (≈ {points} pts)",
    "mc_note": "Comment lire : pts est l'écart de prix, en points d'indice, que le future devrait "
               "avoir au-dessus (+) ou en dessous (−) du forward pour compenser l'effet des "
               "intérêts. C'est le même pour l'acheteur et pour le vendeur.",
    "footnote": "Simplification : une étape = un règlement, et les intérêts sont comptés comme "
                "si une étape durait 1 mois (taux / 12) pour que l'effet soit visible. En "
                "vrai, le règlement est quotidien. La taille des écarts dépend des réglages de "
                "volatilité et n'est qu'illustrative ; leur signe dépend de la corrélation et "
                "de ta position. Outil pédagogique, pas un conseil financier.",

    "intro": "Tu es {position} d'un future S&P 500 (1 point = {point}). La marge initiale est "
             "de {start} : si le compte passe sous {maintenance}, tu dois le recharger (appel "
             "de marge). Choisis la corrélation, puis joue une étape.",
    "position_long": "acheteur",
    "position_short": "vendeur",
    "step_head": "Étape {step} : le S&P {direction} de {pct}.",
    "rises": "monte",
    "falls": "baisse",
    "step_gain": "Tu gagnes {amount}, crédités tout de suite sur ton compte.",
    "step_loss": "Tu perds {amount}, débités tout de suite.",
    "rate_flat": "Le taux ne bouge pas ({rate}).",
    "rate_move": "Le taux {direction} à {rate} : {action} à un taux plus {level}, "
                 "ce qui joue {verdict}.",
    "action_gain": "tu places ce gain",
    "action_loss": "tu finances cette perte",
    "level_up": "haut",
    "level_down": "bas",
    "verdict_good": "en ta faveur",
    "verdict_bad": "contre toi",
    "margin_call": "Compte sous {maintenance} : appel de marge, tu verses {amount} pour "
                   "revenir à {start}.",

    "maturity": "Échéance atteinte. Clique sur « Recommencer » pour rejouer.",
    "auto_done": "Scénario aléatoire joué jusqu'à l'échéance. Regarde l'écart entre future "
                 "et forward plus bas.",
    "network_error": "Impossible de joindre le serveur.",
    "server_error": "Une erreur est survenue.",
    "link_copied": "Lien copié dans le presse-papiers.",
    "link_manual": "Copie ce lien : {url}",

    "tour_stage": "Étape {n} sur {total}",
    "tour_next": "Suivant",
    "tour_finish": "Terminer",
    "tour_exit": "Quitter la visite",
    "tour": [
        {
            "title": "1. Tu achètes un future",
            "text": "Tu viens d'acheter un future sur le S&P 500 à {start_price} points. Chaque "
                    "point vaut {point}, donc le contrat représente {exposure} d'indice. Tu "
                    "n'as rien payé pour le contrat lui-même : tu as seulement mis {start} de "
                    "côté sur ton compte de marge.",
            "question": "As-tu payé {exposure} pour acheter le contrat ?",
            "options": ["Oui, la totalité", "Non, seulement un dépôt (la marge)"],
            "answer": 1,
            "right": "Exact. La marge est un dépôt qui reste à toi, pas le prix du future.",
            "wrong": "Pas tout à fait. La marge est seulement un dépôt qui reste à toi : tu "
                     "n'as pas payé le contrat.",
        },
        {
            "title": "2. Le règlement quotidien",
            "text": "L'indice monte de 2 %, donc le future passe à {price} points. La bourse "
                    "règle tout de suite : {cash} arrivent sur ton compte de marge, pris au "
                    "vendeur d'en face.",
            "question": "D'où vient ce gain ?",
            "options": ["Du vendeur, via la bourse", "De la banque centrale",
                        "La bourse le crée"],
            "answer": 0,
            "right": "Oui. Pour chaque gagnant il y a un perdant : le vendeur paie, et la "
                     "bourse fait passer l'argent.",
            "wrong": "Non. Il vient du vendeur d'en face, via la bourse.",
        },
        {
            "title": "3. Une perte",
            "text": "L'indice baisse de 2 %. {cash} sortent de ton compte. Ton solde est "
                    "maintenant de {balance}, encore au-dessus du seuil d'appel de marge de "
                    "{maintenance}.",
            "question": "As-tu un appel de marge maintenant ?",
            "options": ["Oui", "Non"],
            "answer": 1,
            "right": "Exact : {balance} est au-dessus de {maintenance}.",
            "wrong": "Pas encore : {balance} est encore au-dessus de {maintenance}.",
        },
        {
            "title": "4. L'appel de marge",
            "text": "L'indice baisse encore : {cash}. Ton solde passerait sous {maintenance}, "
                    "donc tu reçois un appel de marge : tu verses {call} pour revenir à "
                    "{start}.",
            "question": "Que te demande un appel de marge ?",
            "options": ["De clôturer le contrat tout de suite",
                        "De déposer du cash pour recharger le compte",
                        "Rien, c'est juste un avertissement"],
            "answer": 1,
            "right": "Oui. C'est juste une recharge de ton dépôt.",
            "wrong": "Non. Tu déposes du cash pour ramener le compte à son niveau de départ.",
        },
        {
            "title": "5. Pourquoi la corrélation compte",
            "text": "L'indice monte de 2 % : tu gagnes {cash} et le taux monte à {rate}, donc "
                    "tu places ce gain à un taux plus haut. Souviens-toi de tes pertes : le "
                    "taux baissait alors, donc tu les as financées à bon prix.",
            "question": "Avec une corrélation positive, que deviennent les intérêts sur tes "
                        "gains et tes pertes ?",
            "options": ["Tu gagnes plus sur les gains et paies moins sur les pertes",
                        "Tu gagnes moins sur les gains et paies plus sur les pertes",
                        "Rien ne change"],
            "answer": 0,
            "right": "Oui. Les gains arrivent avec des taux hauts, les pertes avec des taux "
                     "bas.",
            "wrong": "Non. Avec une corrélation positive, les gains arrivent avec des taux "
                     "hauts et les pertes avec des taux bas.",
        },
        {
            "title": "6. Future contre forward",
            "text": "On joue les étapes restantes au hasard. Sur ce scénario, l'écart entre le "
                    "future et le forward est de {gap}. Un seul scénario dépend du hasard : "
                    "lance les 2 000 scénarios plus bas pour voir la moyenne.",
            "question": "Sur de nombreux scénarios avec une corrélation positive, le future "
                        "vaut ... le forward (pour l'acheteur).",
            "options": ["un peu plus que", "un peu moins que", "exactement autant que"],
            "answer": 0,
            "right": "Oui. L'acheteur gagne un peu plus sur les gains et paie un peu moins "
                     "sur les pertes, donc le prix du future est un peu plus haut que celui "
                     "du forward.",
            "wrong": "Regarde la moyenne sur de nombreux scénarios : avec une corrélation "
                     "positive, l'écart est positif pour l'acheteur.",
        },
    ],
}

TEXT = {"en": EN, "fr": FR}
DEFAULT_LANGUAGE = "en"
