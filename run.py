import random
import google_places_scrapper


def main():
    points_path = 'creating-grid/scrap_points_radius_limit_per_cell_35.csv'
    points = google_places_scrapper.read_points(points_path)
    # random points order:
    points = random.sample(points, 5000)
    scrapper = google_places_scrapper.GooglePlacesScrapper(google_places_scrapper.API_KEY, points)
    scrapper.scrap()


if __name__ == "__main__":
    main()
