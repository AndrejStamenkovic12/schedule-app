# Provider Listing Guide

## How Providers Appear on Service Pages

This guide explains how providers are automatically listed on the correct service category pages in the "Our Services" section.

## Overview

When a provider creates an account or updates their profile with a specific service category, they automatically appear on the corresponding provider page. This is a **fully automated system** - no manual intervention required!

## How It Works

### 1. **During Registration**

When registering as a provider:
1. Fill out the registration form
2. Select your **Service Category** from the dropdown (e.g., "Hair Salon", "Massage Therapy", etc.)
3. Complete the rest of the form and submit
4. You will **immediately appear** on the corresponding provider page!

### 2. **Updating Your Category**

Providers can change their service category anytime:
1. Log in to your provider account
2. Go to **Profile** (or Dashboard → Edit Business Info)
3. Click **Edit Profile**
4. Update the **Service Category** dropdown
5. Click **Save Changes**
6. You'll now appear on the new category's provider page!

## Available Service Categories

### Hair & Beauty
- **Hair Salon** → Shows on `/providers/hair-salon`
- **Nail Salon** → Shows on `/providers/nail-salon`
- **Eyebrow & Eyelash** → Shows on `/providers/eyebrow-eyelash`

### Wellness & Spa
- **Massage Therapy** → Shows on `/providers/massage-therapy`
- **Spa Treatment** → Shows on `/providers/spa-treatment`
- **Aromatherapy** → Shows on `/providers/aromatherapy`

### Fitness & Training
- **Personal Training** → Shows on `/providers/personal-training`
- **Yoga Classes** → Shows on `/providers/yoga-classes`
- **Pilates** → Shows on `/providers/pilates`

### Health & Medical
- **Dermatology** → Shows on `/providers/dermatology`
- **Physical Therapy** → Shows on `/providers/physical-therapy`
- **Nutrition Counseling** → Shows on `/providers/nutrition-consulting`

### Specialty Services
- **Makeup Artist** → Shows on `/providers/makeup-artist`
- **Photography** → Shows on `/providers/photography`
- **Life Coaching** → Shows on `/providers/life-coaching`

## How to Verify Your Listing

### For Providers:
1. Log in to your provider dashboard
2. Look at the **Service Type** section
3. You'll see a link "Listed on: [Your Category] Providers"
4. Click the link to view your listing on the public page

### For Customers:
1. Go to **Services** in the navigation
2. Browse or search for a service category
3. Click **View Providers** on any service card
4. You'll see all registered providers for that category

## Technical Details

### Backend (app.py)
- Each provider has a `service_category` field stored in their user profile
- Provider routes (e.g., `/providers/hair-salon`) filter users by:
  - `role == 'provider'`
  - `service_category == 'hair_salon'`
- The filtering happens automatically when the page loads

### Example Code:
```python
@app.route('/providers/hair-salon')
def hair_providers():
    """View hair salon providers"""
    current_user = get_current_user()
    all_providers = [user for user in user_manager.users if user.get('role') == 'provider']
    hair_providers = [
        {k: v for k, v in provider.items() if k != 'password'}
        for provider in all_providers
        if provider.get('service_category') == 'hair_salon'
    ]
    return render_template('hair_providers.html', providers=hair_providers, current_user=current_user)
```

## Troubleshooting

### "I don't see my business on the provider page"

**Check the following:**
1. Make sure you're logged in as a provider (not a consumer)
2. Verify your **Service Category** is set in your profile
3. Make sure you selected a specific category (not "Other")
4. Try logging out and viewing the page as a guest to see the public view

### "I want to change which page I appear on"

1. Go to your Profile
2. Click **Edit Profile**
3. Change the **Service Category** dropdown
4. Save changes
5. You'll now appear on the new page!

### "I'm in multiple categories"

Currently, each provider can only be in **one primary category**. Choose the category that best represents your main service offering. You can still list multiple services in the "Services Offered" field.

## Quick Test

To test the system:

1. **Register a test provider:**
   ```
   Username: test_hair_salon
   Role: Provider
   Service Category: Hair Salon
   Business Name: Test Hair Studio
   ```

2. **View the listing:**
   - Go to Services → Hair & Beauty → Hair Salon → View Providers
   - OR directly visit: `/providers/hair-salon`
   - You should see "Test Hair Studio" in the list

3. **Update the category:**
   - Edit profile → Change Service Category to "Nail Salon"
   - Save
   - Now visit `/providers/nail-salon` instead
   - Your business now appears here!

## Changes Made

### Files Modified:
1. **app.py** - Added `service_category` to the profile update handler
2. **templates/profile.html** - Added service category dropdown to edit form
3. **templates/provider_dashboard.html** - Added helpful links showing where providers are listed

### Files Already Working:
- All provider routes were already filtering by `service_category`
- Registration form already included service category selection
- Provider listing templates were already set up correctly

The functionality was **mostly already built** - we just needed to:
1. Add the ability to **edit** service category after registration
2. Add **visual feedback** so providers know where they're listed

